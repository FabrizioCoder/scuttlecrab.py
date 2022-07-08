import disnake
import platform
import functools
import luxanna
from disnake.ext import commands
from numerize.numerize import numerize
from luxanna.classes.bot import CustomBot
from luxanna.util.functions.index import *


class Misc(commands.Cog):
    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="ping", help="Pong", aliases=["pong"])
    async def ping(self, ctx: commands.Context) -> None:
        """
        Pong!
        """
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    # Create a help command for the bot
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="help",
        description="Get a list of commands in the bot.",
    )
    async def _help(
        self, interaction: disnake.ApplicationCommandInteraction, command: str = None
    ):
        await interaction.response.defer()
        with open("luxanna/util/commands.json") as json_file:
            COMMANDS = json.load(json_file)

        async def send_help():
            embed_cmds = disnake.Embed(
                title="Luxanna Commands", color=disnake.Color.blurple()
            )
            embed_cmds.set_thumbnail(url=self.bot.user.display_avatar.url)

            for command in COMMANDS["lol"].values():
                embed_cmds.add_field(
                    name=command["name"],
                    value="\n".join(
                        [code_string(command["usage"]), command["description"]]
                    ),
                    inline=True,
                )

            embed_cmds.add_field(
                name="> Links",
                value=" | ".join(
                    [
                        f"[Invite](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=277330906608&scope=bot%20applications.commands)",
                        f"[Support Server](https://discord.gg/pE6efwjXYJ)",
                    ]
                ),
                inline=False,
            )
            return await interaction.edit_original_message(embeds=[embed_cmds])

        if command is None:
            return await send_help()

        if command.lower() in COMMANDS["lol"]:
            embed_cmd = disnake.Embed(
                title=f"{COMMANDS['lol'][command.lower()]['name']} Command",
                color=disnake.Color.blurple(),
                description="\n".join(
                    [
                        COMMANDS["lol"][command.lower()]["description"],
                        f"{code_string('Usage:')} {COMMANDS['lol'][command.lower()]['usage']}",
                    ]
                ),
            )
            embed_cmd.set_thumbnail(url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embeds=[embed_cmd])

        else:
            return await send_help()

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="fetch-invite",
        description="Obtain information from an invitation link for servers",
    )
    async def _fetch_invite(
        self, interaction: disnake.ApplicationCommandInteraction, code: str
    ):
        """
        Parameters
        ----------
        code: The invitation URL (example: https://discord.gg/E6efwjXYJ)
        """

        await interaction.response.defer()

        try:
            invite = await self.bot.fetch_invite(
                url=code, with_counts=True, with_expiration=True
            )

            data = []

            if invite.url:
                data.append(f"{code_string('Invite URL:')} {invite.url}")

            if invite.guild:
                data.append(f"{code_string('Guild:')} {invite.guild.name}")

            if invite.uses:
                data.append(f"{code_string('Uses:')} {invite.uses}")
            else:
                data.append(f"{code_string('Uses:')} Not Found")

            if invite.max_uses:
                data.append(f"{code_string('Max Uses:')} {invite.max_uses}")
            else:
                data.append(f"{code_string('Max Uses:')} Not Found")

            if invite.created_at:
                data.append(
                    f"{code_string('Created At:')} <t:{int(invite.created_at.timestamp())}:R>"
                )
            if invite.expires_at:
                data.append(
                    f"{code_string('Expires At:')} <t:{int(invite.expires_at.timestamp())}:R>"
                )

            if invite.channel:
                data.append(f"{code_string('Channel:')} {invite.channel.mention}")

            embed = disnake.Embed(
                title="Invite Information",
                color=disnake.Color.blurple(),
                description="\n".join(data),
            )
            if invite.guild:
                if invite.guild.icon:
                    embed.set_thumbnail(url=invite.guild.icon.url)

            return await interaction.edit_original_message(embeds=[embed])

        except disnake.errors.NotFound:
            return await interaction.edit_original_message(
                embed=disnake.Embed(
                    title="⚠️ Invite not found",
                    description=f"The invite URL `{code}` was not found.",
                    color=disnake.Color.brand_red(),
                )
            )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="stats",
        description="Get my stats",
    )
    async def _stats(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()

        embed = disnake.Embed(
            title="Luxanna Stats",
            color=disnake.Color.blurple(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        total_users = numerize(
            functools.reduce(lambda c, v: c + v.member_count, self.bot.guilds, 0)
        )
        uptime = int(luxanna.__uptime__.timestamp())

        owner_tags = []
        for id in self.bot.owner_ids:
            user = await self.bot.fetch_user(id)
            if user:
                owner_tags.append(user.name + "#" + user.discriminator)

        desc = [
            f"{code_string('Owners:')} {', '.join(owner_tags)}",
            f"{code_string('Uptime:')} <t:{uptime}:d> (<t:{uptime}:R>)",
            f"{code_string('Total Users:')} {total_users}",
            f"{code_string('Total Servers:')} {numerize(len(self.bot.guilds))}",
        ]

        dependecies_dec = [
            f"{code_string('Pyot:')} 5.1.0",
            f"{code_string('Python:')} {platform.python_version()}",
            f"{code_string('Disnake:')} {disnake.__version__}",
        ]

        embed.description = "\n".join(desc)

        embed.add_field(
            name="> Versions",
            value="\n".join(dependecies_dec),
        )

        return await interaction.edit_original_message(embeds=[embed])

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="invite",
        description="Get an invite link for the bot",
    )
    async def _invite(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        return await interaction.edit_original_message(
            content=f"[Thanks for inviting me](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=277330906608&scope=bot%20applications.commands)",
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="invite",
        description="Get an invite link for the bot",
    )
    async def _invite_cmd(self, ctx: commands.Context):
        return await ctx.send(
            content=f"{bold('Thanks for inviting me')}\nhttps://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=277330906608&scope=bot%20applications.commands",
        )


def setup(bot: CustomBot):
    bot.add_cog(Misc(bot))
    print("✅: Cog loaded: Misc")
