from typing import Literal


PLATFORMS = Literal[
    "LAN", "LAS", "NA", "BR", "EUNE", "EUW", "KR", "JP", "OCE", "RU", "TR"
]

PLATFORM_TO_REGION = {
    "LAN": "la1",
    "LAS": "la2",
    "NA": "na1",
    "BR": "br1",
    "EUNE": "eun1",
    "EUW": "euw1",
    "KR": "kr",
    "JP": "jp1",
    "OCE": "oc1",
    "RU": "ru",
    "TR": "tr1",
}

PLATFORM_TO_REGIONAL = {
    "BR": "AMERICAS",
    "EUNE": "EUROPE",
    "EUW": "EUROPE",
    "JP": "ASIA",
    "KR": "ASIA",
    "LAN": "AMERICAS",
    "LAS": "AMERICAS",
    "NA": "AMERICAS",
    "OCE": "AMERICAS",
    "TR": "EUROPE",
    "RU": "EUROPE",
}

LANES = Literal["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
