from enum import Enum

from dg01.games.digimon.digimon_cog import DigimonCog
from dg01.games.digimon.digimon_data import DigimonDataFields


class GameType(Enum):
    DIGIMON = "디지몬"
    # POKEMON = "포켓몬"
    # YUGIOH = "유희왕"
    # 필요한 게임 타입 추가 가능


MAPPING__GAME_TYPE__COG_CLASS = {
    GameType.DIGIMON: DigimonCog,
}


MAPPING__GAME_TYPE__DATA_FIELDS_CLASS = {
    GameType.DIGIMON: DigimonDataFields,
}



