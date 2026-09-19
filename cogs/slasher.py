from __future__ import annotations

import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from game.auto_hunts import AutoHuntScheduler
from game.hunt_manager import HuntAlreadyActive, HuntManager, NoEligibleVictims
from slashers.registry import SLASHERS, get_slasher, rarity_for


class SetupChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, dashboard: "SlasherSetupView") -> None:
        super().__init__(
            placeholder="Choose the automatic hunt channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text],
            row=2,
        )
        self.dashboard = dashboard

    async def callback(self, interaction: discord.Interaction) -> None:
        if not await self.dashboard.authorized(interaction):
            return

        selected = self.values[0]
        channel_id = selected.id

        self.dashboard.cog.hunts.stats.set_auto_channel(
            self.dashboard.guild_id,
            channel_id,
        )

        # If automatic hunts are already enabled, restart the scheduler so the
        # new channel is used immediately.
        settings = self.dashboard.cog.hunts.stats.get_guild_settings(
            self.dashboard.guild_id
        )
        if settings["auto_enabled"]:
            self.dashboard.cog.auto_hunts.restart(self.dashboard.guild_id)

        await self.dashboard.refresh(interaction)


class SetupFrequencySelect(discord.ui.Select):
    def __init__(self, dashboard: "SlasherSetupView") -> None:
        options = [
            discord.SelectOption(
                label="Testing — 1 to 3 minutes",
                value="1:3",
                description="Useful while building or testing.",
                emoji="🧪",
            ),
            discord.SelectOption(
                label="Frequent — 15 to 45 minutes",
                value="15:45",
                description="Busy servers that want lots of hunts.",
                emoji="⚡",
            ),
            discord.SelectOption(
                label="Balanced — 30 to 90 minutes",
                value="30:90",
                description="Active without becoming constant.",
                emoji="🔪",
            ),
            discord.SelectOption(
                label="Default — 45 to 120 minutes",
                value="45:120",
                description="The original Slasher timing.",
                emoji="🎃",
            ),
            discord.SelectOption(
                label="Slow Burn — 60 to 180 minutes",
                value="60:180",
                description="Less frequent and more surprising.",
                emoji="🌙",
            ),
            discord.SelectOption(
                label="Rare — 120 to 360 minutes",
                value="120:360",
                description="A few hunts across a long session.",
                emoji="🕯️",
            ),
        ]

        super().__init__(
            placeholder="Choose automatic hunt frequency...",
            min_values=1,
            max_values=1,
            options=options,
            row=3,
        )
        self.dashboard = dashboard

    async def callback(self, interaction: discord.Interaction) -> None:
        if not await self.dashboard.authorized(interaction):
            return

        minimum, maximum = (
            int(value)
            for value in self.values[0].split(":", 1)
        )

        self.dashboard.cog.hunts.stats.set_auto_frequency(
            self.dashboard.guild_id,
            minimum,
            maximum,
        )

        # Make the new random window take effect immediately.
        self.dashboard.cog.auto_hunts.restart(self.dashboard.guild_id)

        await self.dashboard.refresh(interaction)


class SlasherSetupView(discord.ui.View):
    def __init__(
        self,
        cog: "SlasherCog",
        guild_id: int,
    ) -> None:
        super().__init__(timeout=600)
        self.cog = cog
        self.guild_id = guild_id

        self.add_item(SetupChannelSelect(self))
        self.add_item(SetupFrequencySelect(self))
        self.sync_button_labels()

    async def authorized(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None or interaction.guild.id != self.guild_id:
            await interaction.response.send_message(
                "This setup panel belongs to a different server.",
                ephemeral=True,
            )
            return False

        member = interaction.user
        permissions = getattr(member, "guild_permissions", None)

        if permissions is None or not permissions.manage_guild:
            await interaction.response.send_message(
                "Only members with **Manage Server** can change these settings.",
                ephemeral=True,
            )
            return False

        return True

    def sync_button_labels(self) -> None:
        settings = self.cog.hunts.stats.get_guild_settings(self.guild_id)

        for item in self.children:
            if not isinstance(item, discord.ui.Button):
                continue

            if item.custom_id == "slasher_setup_auto":
                if settings["auto_enabled"]:
                    item.label = "Auto Hunts: ON"
                    item.style = discord.ButtonStyle.success
                else:
                    item.label = "Auto Hunts: OFF"
                    item.style = discord.ButtonStyle.secondary

            elif item.custom_id == "slasher_setup_ai":
                if settings.get("ai_enabled", False):
                    item.label = "Gemini: ON"
                    item.style = discord.ButtonStyle.success
                else:
                    item.label = "Gemini: OFF"
                    item.style = discord.ButtonStyle.secondary

    async def refresh(self, interaction: discord.Interaction) -> None:
        self.sync_button_labels()

        if interaction.guild is None:
            return

        embed = self.cog._build_setup_embed(interaction.guild)
        await interaction.response.edit_message(
            embed=embed,
            view=self,
        )

    @discord.ui.button(
        label="Auto Hunts: OFF",
        emoji="🔪",
        style=discord.ButtonStyle.secondary,
        custom_id="slasher_setup_auto",
        row=0,
    )
    async def toggle_auto(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if not await self.authorized(interaction):
            return

        settings = self.cog.hunts.stats.get_guild_settings(self.guild_id)
        enabled = not settings["auto_enabled"]

        if enabled and settings["auto_channel_id"] is None:
            if isinstance(interaction.channel, discord.TextChannel):
                self.cog.hunts.stats.set_auto_channel(
                    self.guild_id,
                    interaction.channel.id,
                )
            else:
                await interaction.response.send_message(
                    "Choose a hunt channel below before turning automatic hunts on.",
                    ephemeral=True,
                )
                return

        self.cog.hunts.stats.set_auto_enabled(
            self.guild_id,
            enabled,
        )

        if enabled:
            self.cog.auto_hunts.restart(self.guild_id)
        else:
            self.cog.auto_hunts.stop(self.guild_id)

        await self.refresh(interaction)

    @discord.ui.button(
        label="Gemini: OFF",
        emoji="🧠",
        style=discord.ButtonStyle.secondary,
        custom_id="slasher_setup_ai",
        row=0,
    )
    async def toggle_ai(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if not await self.authorized(interaction):
            return

        settings = self.cog.hunts.stats.get_guild_settings(self.guild_id)
        enabled = not settings.get("ai_enabled", False)

        if enabled and not self.cog.hunts.writer.available:
            await interaction.response.send_message(
                (
                    "Gemini isn't configured yet. Add `GEMINI_API_KEY` "
                    "to `.env`, restart the bot, then try again."
                ),
                ephemeral=True,
            )
            return

        self.cog.hunts.stats.set_ai_enabled(
            self.guild_id,
            enabled,
        )

        await self.refresh(interaction)

    @discord.ui.button(
        label="Refresh",
        emoji="🔄",
        style=discord.ButtonStyle.primary,
        custom_id="slasher_setup_refresh",
        row=0,
    )
    async def refresh_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if not await self.authorized(interaction):
            return

        await self.refresh(interaction)


class SlasherCog(commands.GroupCog, name="slasher"):
    """Commands for The Slasher."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.hunts = HuntManager()
        self.auto_hunts = AutoHuntScheduler(bot, self.hunts)
        super().__init__()

    async def cog_unload(self) -> None:
        self.auto_hunts.stop_all()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # on_ready can fire more than once after reconnects, so ensure_running
        # safely ignores workers that already exist.
        for guild in self.bot.guilds:
            settings = self.hunts.stats.get_guild_settings(guild.id)
            if settings["auto_enabled"]:
                self.auto_hunts.ensure_running(guild.id)

    async def _send_manage_server_error(
        self,
        interaction: discord.Interaction,
    ) -> None:
        message = "Only members with **Manage Server** can change Slasher settings."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


    def _build_setup_embed(
        self,
        guild: discord.Guild,
    ) -> discord.Embed:
        settings = self.hunts.stats.get_guild_settings(guild.id)

        channel = None
        if settings["auto_channel_id"] is not None:
            channel = guild.get_channel(settings["auto_channel_id"])

        channel_text = (
            channel.mention
            if isinstance(channel, discord.TextChannel)
            else "Not set"
        )

        protected_role = discord.utils.get(
            guild.roles,
            name="Slasher Protected",
        )
        protected_text = (
            protected_role.mention
            if protected_role is not None
            else "`Slasher Protected` role not found"
        )

        auto_text = "🟢 ON" if settings["auto_enabled"] else "⚫ OFF"
        ai_text = (
            "🟢 ON"
            if settings.get("ai_enabled", False)
            else "⚫ OFF"
        )

        api_text = (
            "Ready"
            if self.hunts.writer.available
            else "API key not configured"
        )

        embed = discord.Embed(
            title="🔪 THE SLASHER — SERVER SETUP",
            description=(
                f"**Automatic Hunts:** {auto_text}\n"
                f"**Hunt Channel:** {channel_text}\n"
                f"**Random Wait:** {settings['min_minutes']}–"
                f"{settings['max_minutes']} minutes\n"
                f"**Gemini Writer:** {ai_text} ({api_text})\n"
                f"**Fake-outs:** ON • ~8% of random hunts\n"
                f"**Opt-out Role:** {protected_text}\n"
                f"**Killers Loaded:** {len(SLASHERS)}"
            ),
        )

        embed.add_field(
            name="How to use this panel",
            value=(
                "Use the buttons to toggle Auto Hunts or Gemini. "
                "Use the dropdowns below to choose the hunt channel "
                "and random timing."
            ),
            inline=False,
        )

        if protected_role is None:
            embed.add_field(
                name="Optional opt-out role",
                value=(
                    "Create a server role named **Slasher Protected**. "
                    "Anyone with that role will never be selected as a victim."
                ),
                inline=False,
            )

        embed.set_footer(
            text="This control panel is private and only lasts for 10 minutes."
        )
        return embed

    @app_commands.command(
        name="setup",
        description="Open The Slasher's server setup panel.",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_panel(
        self,
        interaction: discord.Interaction,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher setup panel only works inside servers.",
                ephemeral=True,
            )
            return

        view = SlasherSetupView(
            self,
            interaction.guild.id,
        )

        await interaction.response.send_message(
            embed=self._build_setup_embed(interaction.guild),
            view=view,
            ephemeral=True,
        )

    @setup_panel.error
    async def setup_panel_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(name="roster", description="See the killers currently in The Slasher.")
    async def roster(self, interaction: discord.Interaction) -> None:
        lines = [
            (
                f"{slasher.emoji} **{slasher.name}** — "
                f"{slasher.title.title()} • *{rarity_for(slasher.key)}*"
            )
            for slasher in SLASHERS
        ]

        embed = discord.Embed(
            title="🔪 THE SLASHER ROSTER",
            description="\n".join(lines),
        )
        embed.set_footer(text="More killers are coming.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="status", description="Check whether a hunt is active.")
    async def status(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        active = self.hunts.is_active(interaction.guild.id)
        settings = self.hunts.stats.get_guild_settings(interaction.guild.id)

        auto_text = "ON" if settings["auto_enabled"] else "OFF"
        hunt_text = "A hunt is active." if active else "No hunt is active."

        await interaction.response.send_message(
            f"🔪 {hunt_text}\nAutomatic hunts: **{auto_text}**",
            ephemeral=True,
        )

    @app_commands.command(name="stats", description="See your Slasher hunt statistics.")
    @app_commands.describe(member="Optional: see another member's stats")
    async def stats(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "Stats are only available inside a server.",
                ephemeral=True,
            )
            return

        target = member or interaction.user

        data = self.hunts.stats.get_player_stats(
            interaction.guild.id,
            target.id,
        )
        killer_data = self.hunts.stats.get_player_killer_stats(
            interaction.guild.id,
            target.id,
        )

        hunts = data["hunts"]
        survived = data["survived"]
        killed = data["killed"]
        survival_rate = (survived / hunts * 100) if hunts else 0.0

        lines = [
            f"**Hunts:** {hunts}",
            f"**Survived:** {survived}",
            f"**Killed:** {killed}",
            f"**Survival Rate:** {survival_rate:.0f}%",
            f"**Current Survival Streak:** {data['current_streak']}",
            f"**Best Survival Streak:** {data['best_streak']}",
        ]

        if killer_data:
            lines.append("")
            lines.append("**Against Each Killer**")
            for row in killer_data:
                slasher = next(
                    (s for s in SLASHERS if s.key == row["killer_key"]),
                    None,
                )
                killer_name = slasher.name if slasher else row["killer_key"].title()
                lines.append(
                    f"{killer_name}: {row['escapes']} escaped / "
                    f"{row['kills']} killed"
                )

        embed = discord.Embed(
            title=f"🔪 {target.display_name}'s Slasher Stats",
            description="\n".join(lines),
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="See the server's Slasher leaderboard.")
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The leaderboard is only available inside a server.",
                ephemeral=True,
            )
            return

        rows = self.hunts.stats.get_leaderboard(interaction.guild.id)

        if not rows:
            await interaction.response.send_message(
                "Nobody has survived a hunt yet.",
                ephemeral=True,
            )
            return

        lines = []
        for index, row in enumerate(rows, start=1):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"User {row['user_id']}"
            lines.append(
                f"**{index}. {name}** — "
                f"{row['survived']} survived • "
                f"{row['killed']} killed • "
                f"best streak {row['best_streak']}"
            )

        embed = discord.Embed(
            title="🏆 THE SLASHER LEADERBOARD",
            description="\n".join(lines),
        )
        embed.set_footer(text="Ranked by total survivals, then best streak.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="killerstats", description="See how deadly each killer has been.")
    async def killerstats(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "Killer stats are only available inside a server.",
                ephemeral=True,
            )
            return

        rows = self.hunts.stats.get_killer_stats(interaction.guild.id)

        if not rows:
            await interaction.response.send_message(
                "The killers haven't completed any hunts yet.",
                ephemeral=True,
            )
            return

        lines = []
        for row in rows:
            slasher = next(
                (s for s in SLASHERS if s.key == row["killer_key"]),
                None,
            )
            killer_name = slasher.name if slasher else row["killer_key"].title()
            encounters = row["encounters"]
            kill_rate = (row["kills"] / encounters * 100) if encounters else 0.0

            lines.append(
                f"**{killer_name}** — "
                f"{row['kills']} kills • "
                f"{row['escapes']} escapes • "
                f"{kill_rate:.0f}% kill rate"
            )

        embed = discord.Embed(
            title="☠️ KILLER RECORDS",
            description="\n".join(lines),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="auto", description="Turn automatic random hunts on or off.")
    @app_commands.describe(mode="Whether automatic hunts should be on or off")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="On", value="on"),
            app_commands.Choice(name="Off", value="off"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def auto(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str],
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id

        if mode.value == "off":
            self.hunts.stats.set_auto_enabled(guild_id, False)
            self.auto_hunts.stop(guild_id)
            await interaction.response.send_message(
                "🔪 Automatic hunts are now **OFF**.",
                ephemeral=True,
            )
            return

        settings = self.hunts.stats.get_guild_settings(guild_id)

        if settings["auto_channel_id"] is None:
            if not isinstance(interaction.channel, discord.TextChannel):
                await interaction.response.send_message(
                    "Run this command inside the text channel where you want hunts to happen.",
                    ephemeral=True,
                )
                return

            self.hunts.stats.set_auto_channel(
                guild_id,
                interaction.channel.id,
            )

        self.hunts.stats.set_auto_enabled(guild_id, True)
        settings = self.hunts.stats.get_guild_settings(guild_id)
        self.auto_hunts.restart(guild_id)

        channel = interaction.guild.get_channel(settings["auto_channel_id"])
        channel_text = channel.mention if isinstance(channel, discord.TextChannel) else "the configured channel"

        await interaction.response.send_message(
            (
                "🔪 Automatic hunts are now **ON**.\n"
                f"Hunts will appear in {channel_text} after a random wait of "
                f"**{settings['min_minutes']}–{settings['max_minutes']} minutes**."
            ),
            ephemeral=True,
        )

    @auto.error
    async def auto_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(name="channel", description="Choose where automatic hunts appear.")
    @app_commands.describe(channel="The text channel The Slasher should hunt in")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        self.hunts.stats.set_auto_channel(
            interaction.guild.id,
            channel.id,
        )

        await interaction.response.send_message(
            f"🔪 Automatic hunts will happen in {channel.mention}.",
            ephemeral=True,
        )

    @channel.error
    async def channel_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(name="frequency", description="Set the random automatic-hunt time window.")
    @app_commands.describe(
        minimum_minutes="Shortest possible wait before a hunt",
        maximum_minutes="Longest possible wait before a hunt",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def frequency(
        self,
        interaction: discord.Interaction,
        minimum_minutes: app_commands.Range[int, 1, 1440],
        maximum_minutes: app_commands.Range[int, 1, 1440],
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        if minimum_minutes > maximum_minutes:
            await interaction.response.send_message(
                "The minimum wait can't be longer than the maximum wait.",
                ephemeral=True,
            )
            return

        self.hunts.stats.set_auto_frequency(
            interaction.guild.id,
            minimum_minutes,
            maximum_minutes,
        )

        # Restarting makes the new random window take effect immediately rather
        # than waiting for an old timer to finish.
        self.auto_hunts.restart(interaction.guild.id)

        await interaction.response.send_message(
            (
                "⏱️ Automatic hunt timing updated.\n"
                f"The Slasher will wait a random **{minimum_minutes}–"
                f"{maximum_minutes} minutes** between hunts."
            ),
            ephemeral=True,
        )

    @frequency.error
    async def frequency_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(name="autosettings", description="See the automatic hunt settings.")
    async def autosettings(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        settings = self.hunts.stats.get_guild_settings(interaction.guild.id)

        channel = None
        if settings["auto_channel_id"] is not None:
            channel = interaction.guild.get_channel(settings["auto_channel_id"])

        channel_text = channel.mention if isinstance(channel, discord.TextChannel) else "Not set"
        state = "ON" if settings["auto_enabled"] else "OFF"

        embed = discord.Embed(
            title="🔪 AUTOMATIC HUNT SETTINGS",
            description=(
                f"**Automatic Hunts:** {state}\n"
                f"**Channel:** {channel_text}\n"
                f"**Random Wait:** {settings['min_minutes']}–"
                f"{settings['max_minutes']} minutes\n"
                f"**Gemini Writer:** {'ON' if settings.get('ai_enabled', False) else 'OFF'}"
            ),
        )
        embed.set_footer(text="Each completed hunt rolls a brand-new random wait.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(
        name="ai",
        description="Turn Gemini-written hunt scenes on or off.",
    )
    @app_commands.describe(mode="Whether Gemini should write hunt scenes")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="On", value="on"),
            app_commands.Choice(name="Off", value="off"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ai(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str],
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Slasher only uses Gemini inside servers.",
                ephemeral=True,
            )
            return

        if mode.value == "on" and not self.hunts.writer.available:
            await interaction.response.send_message(
                (
                    "⚠️ Gemini is not configured yet. Add `GEMINI_API_KEY` "
                    "to your `.env`, restart The Slasher, then turn AI on."
                ),
                ephemeral=True,
            )
            return

        enabled = mode.value == "on"
        self.hunts.stats.set_ai_enabled(
            interaction.guild.id,
            enabled,
        )

        if enabled:
            message = (
                "🧠 Gemini hunt writing is now **ON**. "
                "Game mechanics still stay under The Slasher's Python engine."
            )
        else:
            message = (
                "📝 Gemini hunt writing is now **OFF**. "
                "The Slasher will use its built-in dialogue pools."
            )

        await interaction.response.send_message(
            message,
            ephemeral=True,
        )

    @ai.error
    async def ai_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(
        name="aistatus",
        description="Check The Slasher's Gemini writer status.",
    )
    async def aistatus(
        self,
        interaction: discord.Interaction,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "Use this command inside a server.",
                ephemeral=True,
            )
            return

        settings = self.hunts.stats.get_guild_settings(interaction.guild.id)
        enabled = settings.get("ai_enabled", False)

        embed = discord.Embed(
            title="🧠 GEMINI WRITER STATUS",
            description=(
                f"**Server Setting:** {'ON' if enabled else 'OFF'}\n"
                f"**API:** {self.hunts.writer.status_text()}\n\n"
                "Gemini writes scene text only. Python still controls "
                "victims, choices, odds, outcomes, stats, and timing."
            ),
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(
        name="aitest",
        description="Ask Gemini to write a sample scene for one killer.",
    )
    @app_commands.describe(killer="Choose which killer Gemini should write")
    @app_commands.choices(
        killer=[
            app_commands.Choice(name="Michael Myers", value="michael"),
            app_commands.Choice(name="Jason Voorhees", value="jason"),
            app_commands.Choice(name="Ghostface", value="ghostface"),
            app_commands.Choice(name="Leatherface", value="leatherface"),
            app_commands.Choice(name="Chucky", value="chucky"),
            app_commands.Choice(name="Captain Spaulding", value="spaulding"),
            app_commands.Choice(name="Art the Clown", value="art"),
            app_commands.Choice(name="Freddy Krueger", value="freddy"),
            app_commands.Choice(name="Candyman", value="candyman"),
            app_commands.Choice(name="Pinhead", value="pinhead"),
            app_commands.Choice(name="Pumpkinhead", value="pumpkinhead"),
            app_commands.Choice(name="Jack Torrance", value="jack"),
            app_commands.Choice(name="Pennywise", value="pennywise"),
            app_commands.Choice(name="Norman Bates", value="norman"),
            app_commands.Choice(name="Xenomorph", value="xenomorph"),
            app_commands.Choice(name="Killer Klowns", value="klowns"),
            app_commands.Choice(name="Deadites", value="deadites"),
            app_commands.Choice(name="Jigsaw", value="jigsaw"),
            app_commands.Choice(name="Leprechaun", value="leprechaun"),
            app_commands.Choice(name="The Thing", value="thing"),
            app_commands.Choice(name="Count Orlok (Nosferatu)", value="nosferatu"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def aitest(
        self,
        interaction: discord.Interaction,
        killer: app_commands.Choice[str],
    ) -> None:
        if not self.hunts.writer.available:
            await interaction.response.send_message(
                "⚠️ Add `GEMINI_API_KEY` to your `.env` and restart the bot first.",
                ephemeral=True,
            )
            return

        slasher = get_slasher(killer.value)
        if slasher is None:
            await interaction.response.send_message(
                "That killer could not be found.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        from game.actions import choices_for_slasher

        script = await self.hunts.writer.generate_script(
            killer_key=slasher.key,
            action_keys=choices_for_slasher(slasher.key),
            rarity=rarity_for(slasher.key),
        )

        if script is None:
            await interaction.followup.send(
                f"⚠️ Gemini did not return a usable script. {self.hunts.writer.status_text()}",
                ephemeral=True,
            )
            return

        preview = discord.Embed(
            title=f"🧠 AI PREVIEW — {slasher.name}",
            description=(
                f"**Intro:** {script.intro}\n"
                f"**Stalk:** {script.stalk}\n"
                f"**Kill:** {script.kill_line}\n"
                f"**Death:** {script.kill_method}\n"
                f"**Escape:** {script.escape_line}"
            ),
        )
        preview.set_footer(text=f"Model: {self.hunts.writer.model}")
        await interaction.followup.send(
            embed=preview,
            ephemeral=True,
        )

    @aitest.error
    async def aitest_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(
        name="huntkiller",
        description="Start a test hunt with a specific killer.",
    )
    @app_commands.describe(killer="Choose which killer should hunt")
    @app_commands.choices(
        killer=[
            app_commands.Choice(name="Michael Myers", value="michael"),
            app_commands.Choice(name="Jason Voorhees", value="jason"),
            app_commands.Choice(name="Ghostface", value="ghostface"),
            app_commands.Choice(name="Leatherface", value="leatherface"),
            app_commands.Choice(name="Chucky", value="chucky"),
            app_commands.Choice(name="Art the Clown", value="art"),
            app_commands.Choice(name="Freddy Krueger", value="freddy"),
            app_commands.Choice(name="Candyman", value="candyman"),
            app_commands.Choice(name="Pinhead", value="pinhead"),
            app_commands.Choice(name="Pumpkinhead", value="pumpkinhead"),
            app_commands.Choice(name="Jack Torrance", value="jack"),
            app_commands.Choice(name="Pennywise", value="pennywise"),
            app_commands.Choice(name="Norman Bates", value="norman"),
            app_commands.Choice(name="Xenomorph", value="xenomorph"),
            app_commands.Choice(name="Killer Klowns", value="klowns"),
            app_commands.Choice(name="Deadites", value="deadites"),
            app_commands.Choice(name="Jigsaw", value="jigsaw"),
            app_commands.Choice(name="Leprechaun", value="leprechaun"),
            app_commands.Choice(name="The Thing", value="thing"),
            app_commands.Choice(name="Count Orlok (Nosferatu)", value="nosferatu"),
            app_commands.Choice(name="Captain Spaulding", value="spaulding"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def huntkiller(
        self,
        interaction: discord.Interaction,
        killer: app_commands.Choice[str],
    ) -> None:
        if interaction.guild is None or interaction.channel is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message(
                "Start the hunt from a text channel.",
                ephemeral=True,
            )
            return

        if self.hunts.is_active(interaction.guild.id):
            await interaction.response.send_message(
                "🔪 There is already a hunt happening in this server.",
                ephemeral=True,
            )
            return

        slasher = get_slasher(killer.value)
        if slasher is None:
            await interaction.response.send_message(
                "That killer couldn't be found.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"🔪 Test hunt starting with **{slasher.name}**...",
            ephemeral=True,
        )

        async def launch() -> None:
            try:
                await self.hunts.run_hunt(
                    interaction.channel,
                    slasher_override=slasher,
                )
            except HuntAlreadyActive:
                pass
            except NoEligibleVictims:
                await interaction.channel.send(
                    "There is nobody eligible for The Slasher to hunt."
                )

        asyncio.create_task(launch())

    @huntkiller.error
    async def huntkiller_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error

    @app_commands.command(name="hunt", description="Manually start a test hunt in this channel.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def hunt(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None or interaction.channel is None:
            await interaction.response.send_message(
                "The Slasher only hunts inside servers.",
                ephemeral=True,
            )
            return

        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            await interaction.response.send_message(
                "Start the hunt from a text channel.",
                ephemeral=True,
            )
            return

        if self.hunts.is_active(interaction.guild.id):
            await interaction.response.send_message(
                "🔪 There is already a hunt happening in this server.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "The lights flicker...",
            ephemeral=True,
        )

        async def launch() -> None:
            try:
                await self.hunts.run_hunt(interaction.channel)
            except HuntAlreadyActive:
                pass
            except NoEligibleVictims:
                await interaction.channel.send(
                    "There is nobody eligible for The Slasher to hunt."
                )

        asyncio.create_task(launch())

    @hunt.error
    async def hunt_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            await self._send_manage_server_error(interaction)
            return
        raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SlasherCog(bot))
