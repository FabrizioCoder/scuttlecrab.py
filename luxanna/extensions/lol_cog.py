import uuid
import disnake
from typing import Dict
from datetime import timedelta
from disnake.ext import commands

from urllib.parse import quote_plus
from numerize.numerize import numerize
from luxanna.util.lol.main import *
from luxanna.util.lol.emojis import *
from luxanna.classes.bot import CustomBot
from luxanna.util.functions.index import *
from luxanna.util.lol.screenshot import Browser
from luxanna.util.lol.champions import CHAMPIONS
from pyot.core.exceptions import (
    NotFound,
    Forbidden,
    RateLimited,
    Unauthorized,
    ServerError,
)


BROWSER = Browser()


class LeagueOfLegends(commands.Cog):
    def __init__(self, bot: CustomBot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def lol(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @commands.cooldown(1, 7, commands.BucketType.user)
    @lol.sub_command(
        name="profile",
        description="Displays information about a summoner: best champions, recent game, master points, etc",
    )
    async def profile(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        region: PLATFORMS = None,
        name: str = None,
    ) -> disnake.InteractionMessage:
        await interaction.response.defer()

        if not region and not name:
            in_db = self.bot.pymongo.get_user_profile(str(interaction.user.id))

            if not in_db:
                return await interaction.edit_original_message(
                    content="⚠️ You do not yet have an account registered to use the no-argument command"
                )

            if in_db:
                region = str(in_db["region"]).upper()
                name = str(in_db["summoner"])

        if not region:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the region of the summoner you want to obtain the information"
            )

        if not name:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the name of the summoner you want to obtain the information"
            )

        parse_name: str = quote_plus(name)
        try:
            summoner = await self.bot.pyot.Summoner(
                name=parse_name, platform=PLATFORM_TO_REGION[region]
            ).get()
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That summoner couldn't be found, at least on that region ({code_string(name)}, {code_string(region)})"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )

        summoner_champion_masteries = await self.bot.pyot.ChampionMasteries(
            summoner_id=summoner.id, platform=PLATFORM_TO_REGION[region]
        ).get()

        summoner_league = await self.bot.pyot.SummonerLeague(
            summoner_id=summoner.id, platform=PLATFORM_TO_REGION[region]
        ).get()

        summoner_match_history = await self.bot.pyot.MatchHistory(
            puuid=summoner.puuid, region=PLATFORM_TO_REGIONAL[region]
        ).get()

        icon = profile_icon(str(summoner.profile_icon_id))

        embed_summoner = disnake.Embed(
            title=f"Luxanna Profile",
            colour=disnake.Colour.blurple(),
        )
        embed_summoner.set_thumbnail(url=icon)
        embed_summoner.add_field(
            name="> Basic Information",
            value="\n".join(
                [
                    f"{code_string('Name:')} {summoner.name}",
                    f"{code_string('Level:')} {summoner.level}",
                    f"{code_string('Platform:')} {region.upper()}",
                    f"{code_string('Icon URL:')} {f'[Click here]({icon})'}",
                ]
            ),
        )
        if len(summoner_champion_masteries) > 0:
            masteries_list_str = []
            for position, champion_mastery in enumerate(
                summoner_champion_masteries.masteries[:3]
            ):
                champion = await champion_mastery.champion.meraki_champion.get()
                masteries_list_str.append(
                    f"{code_string(f'{position+1}:')} {CHAMPION_EMOJIS[champion.name]} {champion.name} (Level {champion_mastery.champion_level}, {bold(numerize(champion_mastery.champion_points))})"
                )

            embed_summoner.add_field(
                name="> Top 3 Champions",
                value="\n".join(masteries_list_str),
            )
        if len(summoner_league.entries) > 0:
            text_solo_duo = italic("Unranked")
            text_flex = italic("Unranked")
            text_tft = italic("Unranked")

            for league in summoner_league.entries:
                if league.queue == "RANKED_SOLO_5x5":
                    if league.wins > 0 and league.losses == 0:
                        solo_duo_winrate = 100.00
                    elif league.wins == 0 and league.losses > 0:
                        solo_duo_winrate = 0.00
                    else:
                        solo_duo_winrate = round(
                            league.wins * 100 / (league.wins + league.losses), 2
                        )
                    text_solo_duo = f'{RANKED_EMOJIS[league.tier.title()]} {bold(league.tier.title())} {bold(league.rank.upper())} ({bold(f"{league.league_points} LP")}) ({bold(f"{league.wins} W")} / {bold(f"{league.losses} L")}, {solo_duo_winrate}%){" "+italic("(Inactive)") if league.inactive else ""}'
                elif league.queue == "RANKED_FLEX_SR":
                    if league.wins > 0 and league.losses == 0:
                        flex_winrate = 100.00
                    elif league.wins == 0 and league.losses > 0:
                        flex_winrate = 0.00
                    else:
                        flex_winrate = round(
                            league.wins * 100 / (league.wins + league.losses), 2
                        )
                    text_flex = f'{RANKED_EMOJIS[league.tier.title()]} {bold(league.tier.title())} {bold(league.rank.upper())} ({bold(f"{league.league_points} LP")}) ({bold(f"{league.wins} W")} / {bold(f"{league.losses} L")}, {flex_winrate}%){" "+italic("(Inactive)") if league.inactive else ""}'
                elif league.queue == "RANKED_TFT":
                    if league.wins > 0 and league.losses == 0:
                        tft_winrate = 100.00
                    elif league.wins == 0 and league.losses > 0:
                        tft_winrate = 0.00
                    else:
                        tft_winrate = round(
                            league.wins * 100 / (league.wins + league.losses), 2
                        )
                    text_tft = f'{RANKED_EMOJIS[league.tier.title()]} {bold(league.tier.title())} {bold(league.rank.upper())} ({bold(f"{league.league_points} LP")}) ({bold(f"{league.wins} W")} / {bold(f"{league.losses} L")}, {tft_winrate}%){" "+italic("(Inactive)") if league.inactive else ""}'

                value = [
                    f"{code_string('Solo/Duo:')} {text_solo_duo}",
                    f"{code_string('Flex:')} {text_flex}",
                    f"{code_string('TFT:')} {text_tft}",
                ]

            embed_summoner.add_field(
                name="> Ranked Stats", value="\n".join(value), inline=False
            )
            if len(summoner_match_history.matches) > 0:
                data = []
                for position, m in enumerate(summoner_match_history.matches[:3]):
                    match = await m.get()
                    summoner_data = None
                    summoner_position = 0
                    for i in [
                        i
                        for i, x in enumerate(match.metadata.participant_puuids)
                        if x == summoner.puuid
                    ]:
                        summoner_position = i + 1
                    for match_participant_data in match.info.participants:
                        if match_participant_data.id == summoner_position:
                            summoner_data = match_participant_data
                    champion_name = (
                        await self.bot.pyot.Champion(id=summoner_data.champion_id).get()
                    ).name
                    created_at = int(match.info.creation.timestamp())
                    data.append(
                        f"{code_string(f'{position+1}:')} {CHAMPION_EMOJIS[champion_name]} {'✅' if summoner_data.win else '❌'} {champion_name} (<t:{created_at}:R>)"
                    )
                embed_summoner.add_field(
                    name="> Recently Played Champions",
                    value="\n".join(data),
                    inline=False,
                )

            if len(summoner_match_history.matches) > 0:
                last_match = await summoner_match_history.matches[0].get()

                summoner_data = None
                summoner_position = 0
                for i in [
                    i
                    for i, x in enumerate(last_match.metadata.participant_puuids)
                    if x == summoner.puuid
                ]:
                    summoner_position = i + 1
                for match_participant_data in last_match.info.participants:
                    if match_participant_data.id == summoner_position:
                        summoner_data = match_participant_data
                champion_name = (
                    await self.bot.pyot.Champion(id=summoner_data.champion_id).get()
                ).name
                k, d, a = (
                    summoner_data.kills,
                    summoner_data.deaths,
                    summoner_data.assists,
                )
                cs = (
                    summoner_data.total_minions_killed
                    + summoner_data.neutral_minions_killed
                )

                game_creation = int(last_match.info.creation.timestamp())

                map = get_map_name_by_id(last_match.info.map_id)

                mode = get_queue_by_id(last_match.info.queue_id)

                embed_summoner.add_field(
                    name="> Last Game",
                    value=f"{bold('✅ Victory') if summoner_data.win else bold('❌ Defeat')} with {bold(champion_name)} {CHAMPION_EMOJIS[champion_name]}, {bold(str(k))}/{bold(str(d))}/{bold(str(a))}{' ('+bold('KDA Perfect')+'), ' if d == 0 and k > 0 else ', '}{bold(f'{cs} CS')}\n{bold(map)}, {mode} (<t:{game_creation}:R>)",
                )

        return await interaction.edit_original_message(embeds=[embed_summoner])

    @commands.cooldown(1, 7, commands.BucketType.user)
    @lol.sub_command(name="champion", description="Get information about a champion")
    async def champion(
        self, interaction: disnake.ApplicationCommandInteraction, name: str
    ):
        """Get information about a champion

        Parameters
        ----------
        **name**: The champion name
        """
        try:
            await interaction.response.defer()
            champion_data = await (
                await self.bot.pyot.Champion(name=name).get()
            ).meraki_champion.get()

            embed_champion = disnake.Embed(
                title=f"{champion_data.name}, {champion_data.title}",
                colour=disnake.Colour.blurple(),
            )
            embed_champion.set_thumbnail(url=champion_data.icon)
            embed_champion.description = (
                f"{champion_data.lore[:3900]}..."
                if len(champion_data.lore) > 3900
                else champion_data.lore
            )

            embed_champion.add_field(
                name="> Price",
                value="\n".join(
                    [
                        f'{ITEM["rp"]} {bold(f"{champion_data.price.rp:,}")} RP',
                        f'{ITEM["blueEssence"]} {bold(f"{champion_data.price.blue_essence:,}")} Blue Essence',
                    ]
                ),
            )
            embed_champion.add_field(
                name="> Tags",
                value=", ".join(champion_data.roles).title()
                if len(champion_data.roles) > 0
                else None,
            )

            skins_values = []
            for skin in champion_data.skins:
                # if skin.cost == 'special':
                #     skin.cost = 0

                skins_values.append(
                    f"[{code_string(skin.format_name)}]({skin.splash_path}) ({ITEM['rp']} {bold(f'{int(skin.cost):,}') if not skin.cost == 'special' else '0 (Special Skin)'} RP)"
                )

            embed_skins = disnake.Embed(
                title=f"{champion_data.name} Skins",
                description="\n".join(skins_values),
                colour=disnake.Colour.blurple(),
            )
            embed_skins.set_thumbnail(url=champion_data.icon)

            embed_abilities = disnake.Embed(
                title=f"{champion_data.name} Abilities",
                colour=disnake.Colour.blurple(),
            )
            embed_abilities.set_thumbnail(url=champion_data.icon)

            if champion_data.abilities:
                if len(champion_data.abilities.p) > 0:
                    pass

            class Buttons(disnake.ui.View):
                def __init__(self):
                    super().__init__(timeout=90)

                @disnake.ui.button(
                    label="Skins",
                    style=disnake.ButtonStyle.blurple,
                    disabled=False,
                )
                async def last_match(
                    self,
                    button: disnake.ui.Button,
                    message_intetaction: disnake.MessageInteraction,
                ):

                    for child in self.children:
                        if isinstance(child, disnake.ui.Button):
                            child.disabled = True
                            await interaction.edit_original_message(view=self)

                    await message_intetaction.send(
                        embeds=[embed_skins], ephemeral=False
                    )
                    self.stop()

                async def on_timeout(
                    self,
                ) -> None:
                    for child in self.children:
                        if isinstance(child, disnake.ui.Button):
                            child.disabled = True
                            await interaction.edit_original_message(view=self)
                    self.stop()

                async def interaction_check(
                    self, msg_interaction: disnake.MessageInteraction
                ) -> bool:
                    if not msg_interaction.author.id == interaction.author.id:
                        await msg_interaction.response.send_message(
                            content="⚠️ You can't use this button",
                            ephemeral=True,
                        )
                        return False
                    return True

            return await interaction.edit_original_message(
                embeds=[embed_champion], view=Buttons()
            )
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That champion couldn't be found"
            )
        except Forbidden:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API request was for an incorrect or unsupported path"
            )
        except RateLimited:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API is rate limited, try again in {code_string(str(30))} seconds"
            )
        except Unauthorized:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: An API key has not been included in the request"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )
        except Exception as _:
            print(f"❌: mastery_subcommand_error: {str(_)}")
            return await interaction.edit_original_message(
                content=f"⚠️ I wasn't able to obtain the information of this champion. I'm very sorry for this (If this error persists, please report it to the developers)"
            )

    @champion.autocomplete("name")
    async def champion_autocomp(
        self, interaction: disnake.ApplicationCommandInteraction, input: str
    ) -> Dict[str, str]:
        string = input.lower()
        return [champ_name for champ_name in CHAMPIONS if string in champ_name.lower()][
            :25
        ]

    @commands.cooldown(1, 7, commands.BucketType.user)
    @lol.sub_command(name="mastery", description="Get a best champions for a summoner")
    async def mastery_subcommand(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        region: PLATFORMS = None,
        name: str = None,
    ):
        await interaction.response.defer()

        if not region and not name:
            in_db = self.bot.pymongo.get_user_profile(str(interaction.user.id))

            if not in_db:
                return await interaction.edit_original_message(
                    content="⚠️ You do not yet have an account registered to use the no-argument command"
                )

            if in_db:
                region = str(in_db["region"]).upper()
                name = str(in_db["summoner"])

        if not region:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the region of the summoner you want to obtain the information"
            )

        if not name:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the name of the summoner you want to obtain the information"
            )

        parse_name: str = quote_plus(name)

        try:
            summoner = await self.bot.pyot.Summoner(
                name=parse_name, platform=PLATFORM_TO_REGION[region]
            ).get()
            summoner_champion_masteries = await self.bot.pyot.ChampionMasteries(
                summoner_id=summoner.id, platform=PLATFORM_TO_REGION[region]
            ).get()

            if len(summoner_champion_masteries.masteries) < 0:
                return await interaction.edit_original_message(
                    content=f"⚠️ This summoner has no champion masteries"
                )

            embed_mastery = disnake.Embed(
                title=f"Best Champions", colour=disnake.Colour.blurple()
            )
            embed_mastery.set_author(
                name=summoner.name, icon_url=profile_icon(str(summoner.profile_icon_id))
            )

            for champion_mastery in summoner_champion_masteries.masteries[:21]:
                champion = await champion_mastery.meraki_champion.get()
                embed_mastery.add_field(
                    name=f"{CHAMPION_EMOJIS[champion.name]} {bold(f'[{str(champion_mastery.champion_level)}]')} - {champion.name}",
                    value=f"{CHEST[champion_mastery.chest_granted]} {bold(numerize(champion_mastery.champion_points))} points",
                )

            return await interaction.edit_original_message(embeds=[embed_mastery])

        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That summoner couldn't be found, at least on that region ({code_string(name)}, {code_string(region)})"
            )
        except Forbidden:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API request was for an incorrect or unsupported path"
            )
        except RateLimited:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API is rate limited, try again in {code_string(str(30))} seconds"
            )
        except Unauthorized:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: An API key has not been included in the request"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )
        except Exception as _:
            print(f"❌: mastery_subcommand_error: {str(_)}")
            return await interaction.edit_original_message(
                content=f"⚠️ I wasn't able to obtain the information of this champion. I'm very sorry for this (If this error persists, please report it to the developers)"
            )

    @commands.cooldown(1, 7, commands.BucketType.user)
    @lol.sub_command(
        name="live", description="Obtaining live game information from a summoner"
    )
    async def live_subcommand(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        region: PLATFORMS = None,
        name: str = None,
    ):
        await interaction.response.defer()

        if not region and not name:
            in_db = self.bot.pymongo.get_user_profile(str(interaction.user.id))

            if not in_db:
                return await interaction.edit_original_message(
                    content="⚠️ You do not yet have an account registered to use the no-argument command"
                )

            if in_db:
                region = str(in_db["region"]).upper()
                name = str(in_db["summoner"])

        if not region:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the region of the summoner you want to obtain the information"
            )

        if not name:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the name of the summoner you want to obtain the information"
            )

        parse_name: str = quote_plus(name)

        try:
            summoner = await self.bot.pyot.Summoner(
                name=parse_name, platform=PLATFORM_TO_REGION[region]
            ).get()
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That summoner couldn't be found, at least on that region ({code_string(name)}, {code_string(region)})"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )

        current_match = None
        try:
            current_match = await self.bot.pyot.CurrentGame(
                summoner_id=summoner.id, platform=PLATFORM_TO_REGION[region]
            ).get()
        except NotFound:
            current_match = None
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )

        if not current_match:
            return await interaction.edit_original_message(
                content=f"⚠️ This summoner is not currently game"
            )

        embed_live = disnake.Embed(
            title=f"Luxanna Live Game", colour=disnake.Colour.blurple()
        )

        icon = profile_icon(str(summoner.profile_icon_id))
        embed_live.set_thumbnail(url=icon)

        # BLUE TEAM
        blue_bans = []
        blue_participants = []

        # RED TEAM
        red_bans = []
        red_participants = []
        for team in current_match.teams:
            if team.id == 100:
                for participant in team.participants:
                    # Blue Spells
                    blue_spells = []
                    for s in participant.spells:
                        spell = await s.get()
                        blue_spells.append(SPELL_EMOJIS_NAME[spell.name])

                    # Blue Participants
                    summoner_champ = await participant.champion.get()
                    t = f"{' - ' if participant.summoner_name == summoner.name else ''}{CHAMPION_EMOJIS[summoner_champ.name]} [{''.join(blue_spells)}] {bold(code_string(participant.summoner_name)) if participant.summoner_name == summoner.name else participant.summoner_name}"
                    blue_participants.append(t)

                    # Blue Bans
                for ban in team.bans:
                    baned_champ = await ban.champion.get()
                    blue_bans.append(
                        f"{CHAMPION_EMOJIS[baned_champ.name]} {bold(baned_champ.name)}"
                    )

            elif team.id == 200:
                for participant in team.participants:
                    # Red Spells
                    red_spells = []
                    for s in participant.spells:
                        spell = await s.get()
                        print(spell.name)
                        red_spells.append(SPELL_EMOJIS_NAME[spell.name])

                    # Red Participants
                    summoner_champ = await participant.champion.get()
                    t = f"{' - ' if participant.summoner_name == summoner.name else ''}{CHAMPION_EMOJIS[summoner_champ.name]} [{''.join(red_spells)}] {bold(code_string(participant.summoner_name)) if participant.summoner_name == summoner.name else participant.summoner_name}"
                    red_participants.append(t)

                    # Red Bans
                for ban in team.bans:
                    baned_champ = await ban.champion.get()
                    red_bans.append(
                        f"{CHAMPION_EMOJIS[baned_champ.name]} {bold(baned_champ.name)}"
                    )

        # embed_live.set_author(name=f"{summoner.name} - {region}", icon_url=icon)
        embed_live.add_field(
            name="> Blue Team", value="\n".join(blue_participants), inline=True
        )
        embed_live.add_field(
            name="> Red Team", value="\n".join(red_participants), inline=True
        )

        if len(blue_bans) and len(red_bans):
            f_blue_bans = list(
                filter(lambda x: x != "<:None:936101187533541466> **None**", blue_bans)
            )
            f_red_bans = list(
                filter(lambda x: x != "<:None:936101187533541466> **None**", red_bans)
            )
            embed_live.add_field(
                name="> Bans",
                value="\n".join(
                    [
                        f'{code_string("Blue:")} {", ".join(f_blue_bans) if len(f_blue_bans) else italic("No available bans for this game mode")}',
                        f'{code_string("Red:")}  {", ".join(f_red_bans) if len(f_red_bans) else italic("No available bans for this game mode")}',
                    ]
                ),
                inline=False,
            )
        map = get_map_name_by_id(current_match.map_id)
        mode = get_queue_by_id(current_match.queue_id)

        embed_live.description = f'{bold(code_string(summoner.name))} ({region.upper()})\nCurrent time: {bold(str(timedelta(seconds=current_match.length_secs)).split(".")[0]) if current_match.length_secs > 0 else bold("Just started playing")}\n{bold(map)}, {mode}'

        return await interaction.edit_original_message(embeds=[embed_live])

    @commands.cooldown(1, 7, commands.BucketType.user)
    @lol.sub_command(
        name="icon", description="Obtaining the profile icon of a summoner"
    )
    async def icon_subcommand(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        region: PLATFORMS = None,
        name: str = None,
    ):
        await interaction.response.defer()

        if not region and not name:
            in_db = self.bot.pymongo.get_user_profile(str(interaction.user.id))

            if not in_db:
                return await interaction.edit_original_message(
                    content="⚠️ You do not yet have an account registered to use the no-argument command"
                )

            if in_db:
                region = str(in_db["region"]).upper()
                name = str(in_db["summoner"])

        if not region:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the region of the summoner you want to obtain the information"
            )

        if not name:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the name of the summoner you want to obtain the information"
            )

        try:

            summoner = await self.bot.pyot.Summoner(
                name=quote_plus(name), platform=PLATFORM_TO_REGION[region]
            ).get()

            icon = profile_icon(str(summoner.profile_icon_id))
            embed = disnake.Embed(
                colour=disnake.Colour.blurple(),
            )
            embed.set_author(name=f"{summoner.name} - {region}", icon_url=icon)
            embed.set_image(url=icon)

            return await interaction.edit_original_message(embeds=[embed])
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That summoner couldn't be found, at least on that region ({code_string(name)}, {code_string(region)})"
            )
        except Forbidden:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API request was for an incorrect or unsupported path"
            )
        except RateLimited:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API is rate limited, try again in {code_string(str(30))} seconds"
            )
        except Unauthorized:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: An API key has not been included in the request"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )
        except Exception as _:
            print(f"❌: icon_subcommand_error: {str(_)}")
            return await interaction.edit_original_message(
                content=f"⚠️ I wasn't able to obtain the icon of this summoner. I'm very sorry for this (If this error persists, please report it to the developers)"
            )

    # Account Group
    @lol.sub_command_group(
        name="account",
        description="Add or remove your LoL account to use the commands without arguments ",
    )
    async def account_subcommand_group(self, interaction):
        pass

    @account_subcommand_group.sub_command(
        name="add", description="Add your League of Legends account to the bot"
    )
    async def account_add_subcommand(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        region: PLATFORMS,
        name: str,
    ):
        await interaction.response.defer()

        try:
            summoner = await self.bot.pyot.Summoner(
                name=quote_plus(name), platform=PLATFORM_TO_REGION[region]
            ).get()
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That summoner couldn't be found, at least on that region ({code_string(name)}, {code_string(region)})"
            )
        except Forbidden:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API request was for an incorrect or unsupported path"
            )
        except RateLimited:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: The API is rate limited, try again in {code_string(str(30))} seconds"
            )
        except Unauthorized:
            return await interaction.edit_original_message(
                content=f"⚠️ {bold(code_string('Internal_Error'))}: An API key has not been included in the request"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )
        except Exception as _:
            print(f"❌: account_add_subcommand_error: {str(_)}")
            return await interaction.edit_original_message(
                content=f"⚠️ I wasn't able to obtain the information of this summoner. I'm very sorry for this (If this error persists, please report it to the developers)"
            )
        summoner_model = self.bot.pymongo.summoners_collection.find_one(
            {"region": region, "summoner": summoner.name}
        )
        user_model = self.bot.pymongo.get_user_profile(str(interaction.author.id))
        if user_model:
            return await interaction.edit_original_message(
                content=f"⚠️ You already have an account on the bot"
            )
        if summoner_model:
            if summoner_model["_id"] == interaction.author.id and user_model:
                return await interaction.edit_original_message(
                    content=f"⚠️ You already have an account on the bot"
                )
            if summoner_model or not summoner_model["_id"] == interaction.author.id:
                return await interaction.edit_original_message(
                    content=f"⚠️ That summoner is already linked to another discord account"
                )
        user_uuid4 = str(uuid.uuid4())
        file = disnake.File("./luxanna/util/example_verify_account.png")
        bot = self.bot

        class Button(disnake.ui.View):
            def __init__(self):
                super().__init__(timeout=90)

            @disnake.ui.button(
                label="Cancel",
                style=disnake.ButtonStyle.red,
                disabled=False,
            )
            async def cancel(
                self,
                button: disnake.ui.Button,
                i: disnake.MessageInteraction,
            ):
                await i.response.send_message(
                    content="✅ You have cancelled the verification process",
                    ephemeral=True,
                )

                await interaction.delete_original_message()
                self.stop()

            @disnake.ui.button(
                label="Verify",
                style=disnake.ButtonStyle.green,
                disabled=False,
            )
            async def verify(
                self,
                button: disnake.ui.Button,
                i: disnake.MessageInteraction,
            ):
                await i.response.defer(ephemeral=True, with_message=True)
                try:
                    third_party_code = await bot.pyot.ThirdPartyCode(
                        summoner_id=summoner.id, platform=PLATFORM_TO_REGION[region]
                    ).get()
                except NotFound:
                    await interaction.delete_original_message()
                    return await i.edit_original_message(
                        content="⚠️ I was unable to verify your account, make sure you entered the code correctly"
                    )
                except Forbidden:
                    return await i.edit_original_message(
                        content=f"⚠️ {bold(code_string('Internal_Error'))}: The API request was for an incorrect or unsupported path"
                    )
                except RateLimited:
                    return await i.edit_original_message(
                        content=f"⚠️ {bold(code_string('Internal_Error'))}: The API is rate limited, try again in {code_string(str(30))} seconds"
                    )
                except Unauthorized:
                    return await i.edit_original_message(
                        content=f"⚠️ {bold(code_string('Internal_Error'))}: An API key has not been included in the request"
                    )
                except ServerError as _:
                    msgs = []
                    for error in _.messages.values():
                        msgs.append(error.message)

                    return await interaction.edit_original_message(
                        content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
                    )
                except Exception as _:
                    print(f"❌: account_add_subcommand_error: {str(_)}")
                    return await i.edit_original_message(
                        content=f"⚠️ I wasn't able to obtain the information of this summoner. I'm very sorry for this (If this error persists, please report it to the developers)"
                    )

                if third_party_code.code == user_uuid4:
                    bot.pymongo.summoners_collection.insert_one(
                        {
                            "region": region,
                            "summoner": summoner.name,
                            "_id": str(interaction.author.id),
                        }
                    )

                    await i.edit_original_message(
                        content="✅ You have verified your account",
                    )

                    await interaction.delete_original_message()
                    return self.stop()
                else:
                    await interaction.delete_original_message()
                    self.stop()
                    return await i.edit_original_message(
                        content="⚠️ I was unable to verify your account, make sure you entered the code correctly",
                        ephemeral=True,
                    )

            async def on_timeout(
                self,
            ) -> None:
                for child in self.children:
                    if isinstance(child, disnake.ui.Button):
                        child.disabled = True
                        await interaction.edit_original_message(view=self)
                self.stop()

            async def interaction_check(
                self, msg_interaction: disnake.MessageInteraction
            ) -> bool:
                if not msg_interaction.author.id == interaction.author.id:
                    await msg_interaction.response.send_message(
                        content="⚠️ You can't use this button",
                        ephemeral=True,
                    )
                    return False
                return True

        message = [
            f'Now go to the settings of your {bold("League of Legends")} client, where you should look for the verification tab',
            "Once there, enter the following code in the window and click save",
            f"> Code: {bold(code_string(user_uuid4))}",
            italic("Time Limit: 90 seconds"),
        ]

        return await interaction.edit_original_message(
            content="\n".join(message),
            files=[file],
            view=Button(),
        )

    @account_subcommand_group.sub_command(
        name="remove",
        description="Remove your account from the bot",
    )
    async def account_remove_subcommand(
        self,
        interaction: disnake.ApplicationCommandInteraction,
    ):
        await interaction.response.defer()

        user_model = self.bot.pymongo.get_user_profile(str(interaction.author.id))

        if not user_model:
            return await interaction.edit_original_message(
                content=f"⚠️ You don't have an account on the bot"
            )

        self.bot.pymongo.summoners_collection.delete_one(
            {"_id": str(interaction.author.id)}
        )

        return await interaction.edit_original_message(
            content="✅ Your account has been removed from the bot"
        )

    @lol.sub_command_group(
        name="server",
        description="Get information about a LoL server (example: LAN, LAS, KR)",
    )
    async def server_subcommand_group(self, interaction):
        pass

    @server_subcommand_group.sub_command(
        name="status",
        description="Get the status of a LoL server (example: LAN, LAS, KR)",
    )
    async def server_status_subcommand(
        self, interaction: disnake.ApplicationCommandInteraction, server: PLATFORMS
    ):
        await interaction.response.defer()

        try:
            status = await self.bot.pyot.Status(
                platform=PLATFORM_TO_REGION[server]
            ).get()

            embed_server_status = disnake.Embed(
                title=f"{server.upper()} ({status.name}) Status",
                colour=disnake.Colour.blurple(),
            )

            if len(status.maintenances) == 0 and len(status.incidents) == 0:
                return await interaction.edit_original_message(
                    content=f"✅ {code_string(f'{server.upper()}:')} No recent issues or events to report",
                )

            if len(status.maintenances) > 0:

                data_maintenances = []
                for status_detail in status.maintenances:
                    for x in status_detail.titles:
                        data_maintenances.append(
                            f"{code_string(f'{status_detail.incident_severity.upper()}:')+ ' ' if status_detail.incident_severity else ''}{x.content}"
                        )
                embed_server_status.add_field(
                    name="> Maintenances",
                    value="\n".join(data_maintenances),
                    inline=False,
                )

            if len(status.incidents) > 0:
                data_incidents = []
                for status_detail in status.incidents:
                    for x in status_detail.titles:
                        data_incidents.append(
                            f"{code_string(f'{status_detail.incident_severity.upper()}:')+ ' ' if status_detail.incident_severity else ''}{x.content}"
                        )
                embed_server_status.add_field(
                    name="> Incidents",
                    value="\n".join(data_incidents),
                    inline=False,
                )

            return await interaction.edit_original_message(
                embeds=[embed_server_status],
            )
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ No data could be obtained from the API"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )

    @lol.sub_command(
        name="matches",
        description="Get the matches of a LoL summoner",
    )
    async def matches_subcommand(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        region: PLATFORMS = None,
        name: str = None,
    ) -> disnake.InteractionMessage:
        await interaction.response.defer()

        if not region and not name:
            in_db = self.bot.pymongo.get_user_profile(str(interaction.user.id))

            if not in_db:
                return await interaction.edit_original_message(
                    content="⚠️ You do not yet have an account registered to use the no-argument command"
                )

            if in_db:
                region = str(in_db["region"]).upper()
                name = str(in_db["summoner"])

        if not region:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the region of the summoner you want to obtain the information"
            )

        if not name:
            return await interaction.edit_original_message(
                content="⚠️ You must specify the name of the summoner you want to obtain the information"
            )

        parse_name: str = quote_plus(name)
        try:
            summoner = await self.bot.pyot.Summoner(
                name=parse_name, platform=PLATFORM_TO_REGION[region]
            ).get()
        except NotFound:
            return await interaction.edit_original_message(
                content=f"⚠️ That summoner couldn't be found, at least on that region ({code_string(name)}, {code_string(region)})"
            )
        except ServerError as _:
            msgs = []
            for error in _.messages.values():
                msgs.append(error.message)

            return await interaction.edit_original_message(
                content=f"⚠️ Service not available from Riot Games API:\n{code_string(str(_.code))}: {', '.join(msgs)}."
            )

        summoner_match_history = await self.bot.pyot.MatchHistory(
            puuid=summoner.puuid, region=PLATFORM_TO_REGIONAL[region]
        ).get()
        embed_summoner_match_history = disnake.Embed(
            title="Luxanna match history",
            colour=disnake.Colour.blurple(),
            description=f"{bold(code_string(summoner.name))} ({region})",
        )
        icon = profile_icon(str(summoner.profile_icon_id))
        embed_summoner_match_history.set_thumbnail(url=icon)
        if len(summoner_match_history.matches) == 0:
            return await interaction.edit_original_message(
                content=f"⚠️ No matches found for {code_string(name)} ({region})"
            )

        if len(summoner_match_history.matches) > 0:
            for position, l_m in enumerate(summoner_match_history.matches[:5]):
                last_match = await l_m.get()
                summoner_data = None
                summoner_position = 0
                for i in [
                    i
                    for i, x in enumerate(last_match.metadata.participant_puuids)
                    if x == summoner.puuid
                ]:
                    summoner_position = i + 1
                for match_participant_data in last_match.info.participants:
                    if match_participant_data.id == summoner_position:
                        summoner_data = match_participant_data
                champion_name = (
                    await self.bot.pyot.Champion(id=summoner_data.champion_id).get()
                ).name
                k, d, a = (
                    summoner_data.kills,
                    summoner_data.deaths,
                    summoner_data.assists,
                )
                cs = (
                    summoner_data.total_minions_killed
                    + summoner_data.neutral_minions_killed
                )
                game_creation = int(last_match.info.creation.timestamp())
                map = get_map_name_by_id(last_match.info.map_id)
                mode = get_queue_by_id(last_match.info.queue_id)
                embed_summoner_match_history.add_field(
                    name=f"> Game #{position + 1}",
                    value=f"{bold('✅ Victory') if summoner_data.win else bold('❌ Defeat')} with {bold(champion_name)} {CHAMPION_EMOJIS[champion_name]}, {bold(str(k))}/{bold(str(d))}/{bold(str(a))}{' ('+bold('KDA Perfect')+'), ' if d == 0 and k > 0 else ', '}{bold(f'{cs} CS')}\n{bold(map)}, {mode} (<t:{game_creation}:R>)",
                    inline=False,
                )
        return await interaction.edit_original_message(
            embeds=[embed_summoner_match_history],
        )


def setup(bot: CustomBot):
    bot.add_cog(LeagueOfLegends(bot))
    print("✅: Cog loaded: LeagueOfLegends")
