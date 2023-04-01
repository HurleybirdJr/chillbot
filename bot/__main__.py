import logging
import logging.handlers
import asyncio
import os
from typing import List, Optional
import discord
from discord.ext import commands
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()


class ChillBot(commands.Bot):
    def __init__(
            self,
            *args,
            initial_extensions: List[str],
            web_client: ClientSession,
            testing_guild_id: Optional[int] = os.getenv("DEBUG_GUILD_ID"),
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def on_ready(self):
        print(f"<{self.user.name} [{self.user.id}] is ready and online!>")

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

        # This would also be a good place to connect to a database


async def main():
    # Logging
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with ClientSession() as our_client:
        # 2. We become responsible for starting the bot.
        print(f"<Starting>")
        extensions = ["members", "fun", "greetings", "events", "moderation", "music"]
        async with ChillBot(commands.when_mentioned,
                            web_client=our_client,
                            initial_extensions=extensions,
                            intents=discord.Intents.all(),
                            activity=discord.Activity(type=discord.ActivityType.listening,
                                                      name="ChillSynth FM",
                                                      url="https://nightride.fm/eq?station=chillsynth"),
                            status=discord.Status.online) as bot:
            await bot.start(os.getenv('TOKEN'))


# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
asyncio.run(main())
