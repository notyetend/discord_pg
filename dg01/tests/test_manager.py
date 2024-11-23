import pytest
import asyncio
from unittest.mock import Mock

from dg01.session import GameSession
from dg01.events import EventBus
from dg01.const import GameType, GameState, create_game_event, GameEvent, GameEventData, GameEventType
from dg01.games.digimon.logic import DigimonLogic
from dg01.errors import GameError
from dg01.manager import GameManager


class TestGameManager:
    @pytest.fixture
    def game_manager(self):
        bot = Mock()
        return GameManager(bot)

    