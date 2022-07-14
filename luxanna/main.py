import disnake
from luxanna.classes.bot import CustomBot

bot = CustomBot()


@bot.event()
async def on_message(message: disnake.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix
    :param message: The message that was sent.
    """

    if message.author == bot.user or message.author.bot:
        return

    if message.guild.me.guild_permissions.manage_messages == False:
        try:
            await message.author.send(
                content=f"❌ Missing `Send Messages` permission in `{message.channel.name}`"
            )
        except:
            return
        return
