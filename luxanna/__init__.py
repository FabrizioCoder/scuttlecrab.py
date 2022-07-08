#!/usr/bin/python
import disnake
import logging
from pathlib import Path
from luxanna.util.config.pyot import *

logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

__productname__ = "Luxanna Crab"
__description__ = "A League of Legends Discord Bot"
__version__ = "2.0"
__repository__ = "https://github.com/FabrizioCoder/luxanna.py"
__author__ = "Fabrizio Iván"
__license__ = "MIT License"
__copyright__ = "Copyright (c) 2022 Fabrizio Iván"
__uptime__ = disnake.utils.utcnow()

ROOT_DIR = Path(__file__).parent
