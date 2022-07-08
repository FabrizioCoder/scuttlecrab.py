import imp
import os
import disnake
from pyot.models import lol
from disnake.ext import commands
from luxanna.classes.pymongo import PyMongoManager

class CustomBot(commands.Bot):
    def __init__(self):
        # Command prefix only applies to message based commands
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=disnake.Intents._from_value(4753),
            # intents=[disnake.Intents.guild_reactions, disnake.Intents.reactions],
            help_command=None,
            owner_ids=[221399196480045056, 686766483350880351],
        )
        self.load_cogs()
        self.pyot = lol
        self.pymongo = PyMongoManager()

    def load_cogs(self):
        # Load all cogs
        for filename in os.listdir("./luxanna/extensions"):
            if filename.endswith(".py"):
                self.load_extension(f"luxanna.extensions.{filename[:-3]}")

    async def on_ready(self):
        """
        Print the bot's login information
        """ """"""
        await self.change_presence(
            activity=disnake.Activity(
                name="The Summoner's Rift", type=disnake.ActivityType.watching
            ),
            status=disnake.Status.do_not_disturb,
        )
        print(f"🤖: Logged in as: {self.user}")

    def init_bot(self):
        self.run(str(os.getenv("BOT_TOKEN")))
