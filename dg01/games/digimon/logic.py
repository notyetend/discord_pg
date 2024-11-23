from dg01.games.base import GameLogic
from dg01.errors import setup_logger, GameError
from dg01.games.digimon.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message


logger = setup_logger(__name__)


class DigimonLogic(GameLogic):
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass
