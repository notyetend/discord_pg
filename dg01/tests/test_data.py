import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from dg01.session import GameSession
from dg01.events import EventBus
from dg01.const import GameType, GameState, create_game_event, GameEvent, GameEventData, GameEventType
from dg01.games.digimon.logic import DigimonLogic
from dg01.errors import GameError
from dg01.manager import GameManager
from dg01.data import GameDataManager

class TestData:
    @pytest.fixture
    def user_id(self):
        return 111
    
    @pytest.fixture
    def channel_id(self):
        return 222

    @pytest.fixture
    def game_type(self):
        return GameType.DIGIMON

    @pytest.fixture
    def game_data_manager(self):
        return GameDataManager()
    
    def test_get_user_data(self, game_data_manager, user_id, channel_id, game_type):
        print(game_data_manager)
        assert game_data_manager.get_user_data(user_id, channel_id)
        