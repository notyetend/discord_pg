import pytest

from dg01.const import create_game_event
from dg01.event_bus import EventBus,  GameEventType
from dg01.game_session import GameSession
from dg01.digimon_config import (
    EVOLUTION_ORDER,
    get_stage_config
)

class TestConfig:
    def test_get_stage_config(self):
        print(EVOLUTION_ORDER)
        