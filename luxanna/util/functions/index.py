import os
import pytz
import json
import disnake
import aioredis
from datetime import datetime
from aiohttp import ClientSession
from luxanna.util.lol.queue import QUEUES
from luxanna.util.lol.maps import MAPS_DATA
from luxanna.util.lol.champions import CHAMPIONS_ID


def code_string(text: str):
    return f"`{text}`"


def code_block(text: str, language: str = "py"):
    return f"```{language}\n{text}```"


def bold(text: str):
    return f"**{text}**"


def italic(text: str):
    return f"*{text}*"


def underline(text: str):
    return f"__{text}__"


def error_embed(
    title: str = '',
    description: str = '',
    color: int = disnake.Colour.brand_red(),
    author: disnake.User = None,
) -> disnake.embeds.Embed:
    IST = pytz.timezone("America/Mexico_City")

    """
    Create an error embed
    """
    embed = disnake.Embed(
        title=title, description=description, color=color, timestamp=datetime.now(IST)
    )
    """
    If author is not None
    """
    if author:
        embed.set_footer(
            text=author.name, icon_url=author.avatar.url or author.default_avatar.url
        )

    """
    Return embed ready to be sent
    """
    return embed


def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
        duration.append("{} days".format(days))
    if hours > 0:
        duration.append("{} hours".format(hours))
    if minutes > 0:
        duration.append("{} minutes".format(minutes))
    if seconds > 0:
        duration.append("{} seconds".format(seconds))

    return ", ".join(duration)


def profile_icon(profileIconId: str) -> str:
    return f"https://ddragon.leagueoflegends.com/cdn/12.12.1/img/profileicon/{profileIconId}.png"


def get_champion_name_by_id(championId: str) -> str:
    def myMapFunc(x):
        boolean = bool(x["value"] == championId)
        if boolean:
            return x

        return None

    for x in filter(myMapFunc, CHAMPIONS_ID):
        return x["name"]


def get_map_name_by_id(map_id: int) -> str:
    def myMapFunc(x):
        boolean = bool(x["mapId"] == int(map_id))
        if boolean:
            return x

        return None

    for x in filter(myMapFunc, MAPS_DATA):
        return x["mapName"]


def get_queue_by_id(id: int) -> str:
    def myMapFunc(x):
        boolean = bool(x["queueId"] == int(id))
        if boolean:
            return x

        return None

    for x in filter(myMapFunc, QUEUES):
        return x["description"]


async def fetch_items():
    redis = await aioredis.create_redis("redis://localhost", timeout=15)

    has = await redis.get("items")
    if has:
        return json.loads(has)

    session = ClientSession()
    async with session.get(os.getenv("CDN_ITEMS")) as response:
        data = await response.json()
    await session.close()

    await redis.set("items", json.dumps(data))
    # redis.close()
    return data


async def get_item_id_by_name(name: str):
    items = await fetch_items()
    for id, value in items.items():
        if value["name"] == name:
            return value["id"]


def paginate(text: str) -> list[str]:
    last = 0
    pages: list[str] = []
    for curr in range(0, len(text)):
        if curr % 1930 == 0:
            pages.append(text[last:curr])
            last = curr
            appd_index = curr
    if appd_index != len(text) - 1:
        pages.append(text[last:curr])
    return list(filter(lambda a: a != "", pages))
