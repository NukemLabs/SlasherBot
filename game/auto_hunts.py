from __future__ import annotations

import asyncio
import random

import discord
from discord.ext import commands

from game.hunt_manager import HuntAlreadyActive, HuntManager, NoEligibleVictims


class AutoHuntScheduler:
    def __init__(self, bot: commands.Bot, hunts: HuntManager) -> None:
        self.bot = bot
        self.hunts = hunts
        self._tasks: dict[int, asyncio.Task] = {}

    def ensure_running(self, guild_id: int) -> None:
        task = self._tasks.get(guild_id)

        if task is not None and not task.done():
            return

        self._tasks[guild_id] = asyncio.create_task(
            self._worker(guild_id),
            name=f"slasher-auto-{guild_id}",
        )

    def stop(self, guild_id: int) -> None:
        task = self._tasks.pop(guild_id, None)
        if task is not None and not task.done():
            task.cancel()

    def restart(self, guild_id: int) -> None:
        self.stop(guild_id)

        settings = self.hunts.stats.get_guild_settings(guild_id)
        if settings["auto_enabled"]:
            self.ensure_running(guild_id)

    def stop_all(self) -> None:
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
        self._tasks.clear()

    async def _worker(self, guild_id: int) -> None:
        try:
            while True:
                settings = self.hunts.stats.get_guild_settings(guild_id)

                if not settings["auto_enabled"]:
                    return

                channel_id = settings["auto_channel_id"]
                if channel_id is None:
                    return

                min_minutes = settings["min_minutes"]
                max_minutes = settings["max_minutes"]

                wait_seconds = random.randint(
                    min_minutes * 60,
                    max_minutes * 60,
                )

                await asyncio.sleep(wait_seconds)

                # Re-read settings because admins may have changed them while
                # this worker was sleeping.
                settings = self.hunts.stats.get_guild_settings(guild_id)

                if not settings["auto_enabled"]:
                    return

                channel_id = settings["auto_channel_id"]
                channel = self.bot.get_channel(channel_id)

                if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                    continue

                # If a manual hunt is already happening, skip this attempt and
                # roll a brand-new random delay instead of stacking hunts.
                if self.hunts.is_active(guild_id):
                    continue

                try:
                    await self.hunts.run_hunt(channel)
                except (HuntAlreadyActive, NoEligibleVictims):
                    continue
                except (discord.Forbidden, discord.HTTPException):
                    # Permissions or a temporary Discord error should not kill
                    # the scheduler. It will try again after another random wait.
                    continue

        except asyncio.CancelledError:
            raise
        finally:
            current = self._tasks.get(guild_id)
            if current is asyncio.current_task():
                self._tasks.pop(guild_id, None)
