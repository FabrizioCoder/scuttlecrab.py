import os
import platform
from dotenv import load_dotenv
from pyot.conf.model import activate_model, ModelConf
from pyot.conf.pipeline import activate_pipeline, PipelineConf

load_dotenv()

if platform.system() == "Windows":
    from pyot.utils.runtime import silence_proactor_pipe_deallocation

    silence_proactor_pipe_deallocation()


@activate_model("riot")
class RiotModel(ModelConf):
    default_platform = "na1"
    default_region = "americas"
    default_version = "latest"
    default_locale = "en_us"


@activate_model("lol")
class LolModel(ModelConf):
    default_platform = "na1"
    default_region = "americas"
    default_version = "latest"
    default_locale = "en_us"


@activate_pipeline("lol")
class LolPipeline(PipelineConf):
    name = "lol_main"
    default = True
    stores = [
        {
            "backend": "pyot.stores.omnistone.Omnistone",
            "log_level": 0,
            "expirations": {
                "summoner_v4_by_name": 100,
                "match_v5_match": 600,
                "match_v5_timeline": 600,
            },
        },
        {
            "backend": "pyot.stores.merakicdn.MerakiCDN",
            "log_level": 0,
            "error_handler": {404: ("T", []), 500: ("R", [3])},
        },
        {
            "backend": "pyot.stores.cdragon.CDragon",
            "log_level": 0,
            "error_handler": {404: ("T", []), 500: ("R", [3])},
        },
        {
            "backend": "pyot.stores.riotapi.RiotAPI",
            "api_key": os.getenv("RIOT_API_KEY"),
            "log_level": 0,
            "error_handler": {400: ("T", []), 503: ("E", [3, 3])},
            # "rate_limiter": {
            #     "backend": "pyot.limiters.redis.RedisLimiter",
            #     "limiting_share": 1,
            #     "host": "localhost",
            #     "port": 6379,
            #     "db": 0,
            # },
        },
        # {
        #     "backend": "pyot.stores.rediscache.RedisCache",
        #     "host": "localhost",
        #     "log_level": 0,
        #     "port": 6379,
        #     "db": 0,
        #     "expirations": {
        #         "summoner_v4_by_name": 90,
        #         "match_v5_match": 180,
        #         # "match_v5_timeline": 600,
        #         "league_v4_challenger_league": 600,
        #     },
        # },
    ]
