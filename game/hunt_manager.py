from __future__ import annotations

import asyncio
import logging
import random
from collections import defaultdict, deque

import discord

from game.actions import (
    ACTIONS,
    adjusted_kill_chance,
    choice_footer,
    choices_for_slasher,
    reaction_lines,
)
from game.database import StatsDatabase
from game.card_renderer import render_hunt_card
from game.gemini_writer import AIHuntScript, GeminiWriter
from game.presentation import (
    fakeout_text,
    fakeout_title,
    pick_escape_line,
    pick_intro,
    pick_kill_line,
    pick_stalk,
    rarity_color,
    rarity_footer,
    should_fakeout,
    survival_bonus_text,
    warning_title,
)
from slashers.base import Slasher
from slashers.registry import random_slasher, rarity_for


logger = logging.getLogger(__name__)


class HuntAlreadyActive(Exception):
    pass


class NoEligibleVictims(Exception):
    pass


class HuntActionButton(discord.ui.Button):
    def __init__(self, action_key: str) -> None:
        action = ACTIONS[action_key]

        style_map = {
            "run": discord.ButtonStyle.success,
            "hide": discord.ButtonStyle.primary,
            "fight": discord.ButtonStyle.danger,
            "solve_box": discord.ButtonStyle.primary,
            "wake_up": discord.ButtonStyle.success,
            "stay_silent": discord.ButtonStyle.primary,
            "say_name": discord.ButtonStyle.danger,
            "beg": discord.ButtonStyle.secondary,
        }

        super().__init__(
            label=action.label,
            emoji=action.emoji,
            style=style_map.get(action_key, discord.ButtonStyle.secondary),
        )
        self.action_key = action_key

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if isinstance(view, HuntChoiceView):
            await view.choose(interaction, self.action_key)


class HuntChoiceView(discord.ui.View):
    def __init__(
        self,
        victim_id: int,
        action_keys: tuple[str, ...],
        *,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.victim_id = victim_id
        self.selected_action: str | None = None

        for action_key in action_keys:
            self.add_item(HuntActionButton(action_key))

    async def choose(self, interaction: discord.Interaction, action_key: str) -> None:
        if interaction.user.id != self.victim_id:
            await interaction.response.send_message(
                "🔪 You're not the one being hunted.",
                ephemeral=True,
            )
            return

        if self.selected_action is not None:
            await interaction.response.send_message(
                "You've already made your choice.",
                ephemeral=True,
            )
            return

        self.selected_action = action_key

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        # Only update the buttons here.
        #
        # Editing an embed that uses an attachment:// image can make Discord
        # briefly surface that attachment as a large standalone image. Keeping
        # the embed untouched prevents that visual jump while still locking
        # the victim's choice immediately.
        await interaction.response.edit_message(view=self)
        self.stop()

class HuntManager:
    def __init__(self) -> None:
        self._active_guilds: set[int] = set()
        self._recent_victims: dict[int, deque[int]] = defaultdict(
            lambda: deque(maxlen=3)
        )
        self.stats = StatsDatabase()
        self.writer = GeminiWriter()

    def is_active(self, guild_id: int) -> bool:
        return guild_id in self._active_guilds

    async def _eligible_members(self, guild: discord.Guild) -> list[discord.Member]:
        if not guild.chunked:
            try:
                await guild.chunk(cache=True)
            except (discord.HTTPException, discord.ClientException):
                pass

        protected_role = discord.utils.get(guild.roles, name="Slasher Protected")
        recent = set(self._recent_victims[guild.id])

        eligible: list[discord.Member] = []

        for member in guild.members:
            if member.bot:
                continue
            if member.pending:
                continue
            if protected_role and protected_role in member.roles:
                continue
            if member.id in recent:
                continue
            eligible.append(member)

        if not eligible:
            for member in guild.members:
                if member.bot or member.pending:
                    continue
                if protected_role and protected_role in member.roles:
                    continue
                eligible.append(member)

        return eligible

    async def choose_victim(self, guild: discord.Guild) -> discord.Member:
        members = await self._eligible_members(guild)
        if not members:
            raise NoEligibleVictims
        return random.choice(members)

    async def run_hunt(
        self,
        channel: discord.TextChannel | discord.Thread,
        slasher_override: Slasher | None = None,
    ) -> tuple[discord.Member, Slasher, bool]:
        guild = channel.guild

        if guild.id in self._active_guilds:
            raise HuntAlreadyActive

        self._active_guilds.add(guild.id)

        try:
            victim = await self.choose_victim(guild)
            slasher = slasher_override or random_slasher()

            rarity = rarity_for(slasher.key)
            action_keys = choices_for_slasher(slasher.key)

            ai_script: AIHuntScript | None = None
            settings = self.stats.get_guild_settings(guild.id)

            if settings.get("ai_enabled", False):
                ai_script = await self.writer.generate_script(
                    killer_key=slasher.key,
                    action_keys=action_keys,
                    rarity=rarity,
                )

            intro = (
                ai_script.intro
                if ai_script is not None
                else pick_intro(slasher)
            )
            stalk = (
                ai_script.stalk
                if ai_script is not None
                else pick_stalk(slasher)
            )

            intro_discord = intro.replace("{victim}", victim.mention)
            stalk_discord = stalk.replace("{victim}", victim.mention)
            stalk_card = stalk.replace(
                "{victim}",
                f"@{victim.display_name}",
            )

            # Rarely, a normal/random hunt becomes a one-message fake-out.
            # Specific /slasher huntkiller tests always run the full encounter.
            if should_fakeout(slasher_override):
                fakeout = (
                    ai_script.fakeout_line.replace("{victim}", victim.mention)
                    if ai_script is not None
                    else fakeout_text(slasher.key, victim.mention)
                )
                if fakeout:
                    fake_embed = discord.Embed(
                        title=fakeout_title(slasher),
                        description=(
                            f"{fakeout}\n\n"
                            "**No attack came. This time.**"
                        ),
                        color=rarity_color(rarity),
                    )
                    fake_embed.set_footer(
                        text=f"{rarity} appearance • No hunt stats recorded."
                    )
                    await channel.send(embed=fake_embed)
                    self._recent_victims[guild.id].append(victim.id)
                    return victim, slasher, False

            warning = discord.Embed(
                title=warning_title(slasher.key, rarity),
                description=intro_discord,
                color=rarity_color(rarity),
            )
            warning.set_footer(text=rarity_footer(rarity))
            await channel.send(embed=warning)

            await asyncio.sleep(random.uniform(4.0, 7.0))

            view = HuntChoiceView(
                victim.id,
                action_keys,
                timeout=30.0,
            )

            hunt_embed = discord.Embed(
                title=f"{slasher.emoji} WHAT DO YOU DO?",
                description=(
                    f"{victim.mention}, **{slasher.name}** is hunting you.\n"
                    f"*{stalk_discord}*\n\n"
                    "**Choose quickly.**"
                ),
                color=rarity_color(rarity),
            )
            hunt_embed.set_footer(
                text=f"{choice_footer(slasher.key)} • {rarity} encounter"
            )

            card_file: discord.File | None = None

            try:
                card_buffer = await asyncio.to_thread(
                    render_hunt_card,
                    victim_name=victim.display_name,
                    killer_name=slasher.name,
                    scene=stalk_card,
                    action_labels=tuple(
                        ACTIONS[key].label
                        for key in action_keys
                    ),
                )

                card_file = discord.File(
                    card_buffer,
                    filename="slasher_hunt.jpg",
                )
                hunt_embed.set_image(
                    url="attachment://slasher_hunt.jpg"
                )
            except Exception:
                logger.exception(
                    "Could not render VHS hunt card for guild %s.",
                    guild.id,
                )

            if card_file is not None:
                hunt_message = await channel.send(
                    embed=hunt_embed,
                    view=view,
                    file=card_file,
                )
            else:
                # The game still works if the card renderer ever fails.
                hunt_message = await channel.send(
                    embed=hunt_embed,
                    view=view,
                )

            timed_out = await view.wait()

            action_key = view.selected_action
            if timed_out or action_key is None:
                action_key = "freeze"

                for item in view.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True

                action = ACTIONS[action_key]
                hunt_embed.title = f"{action.emoji} TOO LATE"
                hunt_embed.description = (
                    f"{victim.mention} didn't choose in time.\n\n"
                    f"*{action.description}*"
                )
                hunt_embed.set_footer(text="The Slasher closes in...")
                await hunt_message.edit(embed=hunt_embed, view=view)

            await asyncio.sleep(random.uniform(3.0, 5.0))

            ai_reaction = (
                ai_script.reaction_for(action_key)
                if ai_script is not None
                else None
            )
            reaction = (
                ai_reaction.replace("{victim}", victim.mention)
                if ai_reaction
                else random.choice(reaction_lines(slasher.key, action_key))
            )
            action = ACTIONS[action_key]

            hunt_embed.title = f"{slasher.emoji} THE SLASHER REACTS"
            hunt_embed.description = (
                f"{victim.mention} chose **{action.label}**.\n\n"
                f"*{reaction}*"
            )
            hunt_embed.set_footer(text="Your fate is being decided...")
            await hunt_message.edit(embed=hunt_embed, view=view)

            await asyncio.sleep(random.uniform(3.0, 5.0))

            kill_chance = adjusted_kill_chance(
                slasher.key,
                slasher.kill_chance,
                action_key,
            )
            killed = random.random() < kill_chance

            if killed:
                if ai_script is not None:
                    line = ai_script.kill_line.replace("{victim}", victim.mention)
                    method = ai_script.kill_method.replace("{victim}", victim.mention)
                else:
                    line = pick_kill_line(slasher, victim.mention)
                    method = random.choice(tuple(slasher.kill_methods))

                hunt_embed.title = f"☠️ KILLED BY {slasher.name.upper()}"
                hunt_embed.description = (
                    f"{line}\n\n"
                    f"**Cause of death:** {method}\n\n"
                    f"**☠️ {victim.mention} WAS KILLED**"
                )
                hunt_embed.set_footer(
                    text=f"Choice: {action.label} • The Slasher disappears into the darkness."
                )
            else:
                line = (
                    ai_script.escape_line.replace("{victim}", victim.mention)
                    if ai_script is not None
                    else pick_escape_line(slasher, victim.mention)
                )
                bonus = survival_bonus_text(rarity)
                hunt_embed.title = "🏃 THEY GOT AWAY!"
                hunt_embed.description = (
                    f"{line}\n\n"
                    f"**✅ {victim.mention} SURVIVED**"
                    f"{bonus}"
                )
                hunt_embed.set_footer(
                    text=f"Choice: {action.label} • {slasher.name} vanishes... for now."
                )

            await hunt_message.edit(embed=hunt_embed, view=None)

            self.stats.record_hunt(
                guild.id,
                victim.id,
                slasher.key,
                killed,
            )

            self._recent_victims[guild.id].append(victim.id)
            return victim, slasher, killed

        finally:
            self._active_guilds.discard(guild.id)
