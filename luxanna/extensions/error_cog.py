import sys
import traceback
from disnake.ext import commands
from luxanna.util.functions.index import *
from luxanna.classes.bot import CustomBot


def seconds2str(time):
    time = int(time)

    s = time % 60
    time = int((time - s) / 60)
    m = time % 60
    time = int((time - m) / 60)
    h = time % 24
    d = int((time - h) / 24)

    if d > 0:
        return f"{d}d, {h:02}:{m:02}:{s:02}"
    if h > 0:
        return f"{h}:{m:02}:{s:02}"
    if m > 0:
        return f"{m}:{s:02}"
    return f"{s} seconds"


class Errors(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    # @commands.Bot.event
    # async def on_message(message: disnake.Message) -> None:
    #     """
    #     The code in this event is executed every time someone sends a message, with or without the prefix
    #     :param message: The message that was sent.
    #     """

    #     if message.author == message.guild.me._user or message.author.bot:
    #         return

    #     if message.guild.me.guild_permissions.manage_messages == False:
    #         try:
    #             await message.author.send(
    #                 content=f"❌ Missing `Send Messages` permission in `{message.channel.name}`"
    #             )
    #         except:
    #             return
    #         return

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        print(error)
        # Ignore local handlers
        if hasattr(ctx.command, "on_error"):
            return

        # Get original exception
        error = getattr(error, "original", error)

        # Handle messages with prefix
        if isinstance(error, commands.CommandNotFound):
            return

        # User interaction
        elif isinstance(error, commands.NotOwner):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(ctx, error, "You are not an owner")

        elif isinstance(error, commands.MissingRequiredArgument):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(
                    ctx,
                    error,
                    f"Missing required argument: {code_string(error.param.name)}",
                )

        elif isinstance(error, commands.BadArgument):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(
                    ctx,
                    error,
                    f"{code_string(str(error.argument))} is not a valid argument",
                )

        elif isinstance(error, commands.ArgumentParsingError):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(ctx, error, "Bad argument quotes")

        elif isinstance(error, commands.BotMissingPermissions):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(
                    ctx, error, "Wormhole does not have permission to do this"
                )

        elif isinstance(error, commands.CheckFailure):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(ctx, error, "You are not allowed to do this")

        elif isinstance(error, commands.CommandOnCooldown):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(
                    ctx,
                    error,
                    f"This command is on cooldown, try in {code_string(seconds2str(error.retry_after))}",
                )

        elif isinstance(error, commands.UserInputError):
            if not ctx.guild.me.guild_permissions.send_messages:
                return await self.send(ctx, error, "Wrong input")

        # Cog loading
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            return print(f"The cog is already loaded:\n{error}")
        elif isinstance(error, commands.ExtensionNotLoaded):
            return print(f"The cog is not loaded")
        elif isinstance(error, commands.ExtensionFailed):
            await self.send(ctx, error, "The cog failed")
        elif isinstance(error, commands.ExtensionNotFound):
            return await self.send(ctx, error, "No such cog")

        # print the rest
        s = "Wormhole error: {prefix}{command} by {author} in {channel}".format(
            prefix="'",
            command=ctx.command,
            author=str(ctx.author),
            channel=ctx.channel.id
            if hasattr(ctx.channel, "id")
            else type(ctx.channel).__name__,
        )
        print(s, file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )
        if not ctx.guild.me.guild_permissions.send_messages:
            await self.send(ctx, error, str(error))

    @commands.Cog.listener()
    async def on_slash_command_error(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        exception: commands.CommandError,
    ):
        if isinstance(exception, commands.CommandOnCooldown):
            return await interaction.send(
                f"⚠️ This command is on cooldown, try in {code_string(seconds2str(exception.retry_after))}",
                ephemeral=True,
            )

        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=sys.stderr
        )
        await interaction.send(
            f"⚠️ Something has happened:\n{code_block(exception)}", ephemeral=True
        )

    async def send(self, ctx: commands.Context, error, text: str):
        embed = error_embed(
            title="⚠️ Something has happened",
            description=text,
            color=disnake.Colour.brand_red(),
            author=ctx.author,
        )
        if not ctx.guild.me.guild_permissions.send_messages:
            await ctx.send(embeds=[embed])


def setup(bot: CustomBot):
    bot.add_cog(Errors(bot))
    print("✅: Cog loaded: Errors")
