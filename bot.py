import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

TOKEN = os.getenv("DISCORD_TOKEN")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")


class SlasherBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.none()
        intents.guilds = True
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=False,
                users=True,
                replied_user=False,
            ),
        )

    async def setup_hook(self) -> None:
        await self.load_extension("cogs.slasher")

        if DEV_GUILD_ID:
            guild = discord.Object(id=int(DEV_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logging.info(
                "Synced %s command(s) to development guild %s.",
                len(synced),
                DEV_GUILD_ID,
            )
        else:
            synced = await self.tree.sync()
            logging.info(
                "Synced %s global command(s).",
                len(synced),
            )

    async def on_ready(self) -> None:
        if self.user is None:
            return

        logging.info(
            "The Slasher is online as %s (%s)",
            self.user,
            self.user.id,
        )

        await self.change_presence(
            activity=discord.Game(name="watching from the shadows")
        )


def main() -> None:
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN is missing. Add it to your .env file."
        )

    bot = SlasherBot()
    bot.run(TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
