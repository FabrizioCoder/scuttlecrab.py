import io
import disnake
import textwrap
import traceback
import contextlib
from typing import List
from disnake.ext import commands
from luxanna.classes.bot import CustomBot
from luxanna.util.functions.index import *


class PaginatorButton(disnake.ui.View):
    def __init__(self, pages: List[str]):
        super().__init__(
            timeout=20,
        )
        self.pages = pages
        self.pages_count = 0

        self.first_page.disabled = True
        self.prev_page.disabled = True

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.pages_count = 0
        page = self.pages[self.pages_count]

        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        await interaction.response.edit_message(content=code_block(page), view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.pages_count -= 1
        page = self.pages[self.pages_count]

        self.next_page.disabled = False
        self.last_page.disabled = False
        if self.pages_count == 0:
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(content=code_block(page), view=self)

    @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red)
    async def remove(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.pages_count += 1
        page = self.pages[self.pages_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.pages_count == len(self.pages) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(content=code_block(page), view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.pages_count = len(self.pages) - 1
        page = self.pages[self.pages_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        await interaction.response.edit_message(content=code_block(page), view=self)


class Dev(commands.Cog):
    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot

    @commands.command(
        name="eval",
        help="Evaluate Python code.",
    )
    @commands.is_owner()
    async def eval_command(self, ctx: commands.Context, *, code: str) -> None:
        """
        Evaluate Python code.
        """
        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:-1])
        else:
            code = code.strip("` \n")

        variables = {
            "os": os,
            "db": self.bot.pymongo,
            "lol": self.bot.pyot,
            "bot": ctx.bot,
            "ctx": ctx,
            "guild": ctx.guild,
            "author": ctx.author,
            "prefix": ctx.prefix,
            "channel": ctx.channel,
            "message": ctx.message,
        }
        variables.update(globals())

        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f'async def _eval():\n{textwrap.indent(code, "    ")}',
                    variables,
                )

                obj = await variables["_eval"]()
                result = "\n".join([stdout.getvalue(), f"-> {obj}"])
        except Exception as _:
            result = traceback.format_exc()

        pages = paginate(result)

        if not ctx.guild.me.guild_permissions.send_messages:
            return await ctx.send(
                content=code_block(pages[0]),
                view=PaginatorButton(pages),
            )


def setup(bot: CustomBot) -> None:
    bot.add_cog(Dev(bot))
    print("✅: Cog loaded: Dev")
