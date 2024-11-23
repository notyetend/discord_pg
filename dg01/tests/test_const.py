import pytest
import asyncio
from unittest.mock import MagicMock
from dataclasses import fields

from dg01.const import create_game_event, GameType, GameEventDefaultData
from dg01.events import EventBus,  GameEventType
from dg01.session import GameSession


class TestConst:
    @pytest.fixture
    def user_id(self):
        return 111

    @pytest.fixture
    def channel_id(self):
        return 222

    @pytest.fixture
    def event_bus(self):
        return EventBus()

    @pytest.fixture
    def game_type(self):
        return GameType.DIGIMON

    @pytest.fixture
    def game_session(self, user_id, channel_id, event_bus, game_type):
        return GameSession(user_id, channel_id, event_bus, game_type)

    @pytest.mark.asyncio
    async def test_create_game_event(self, game_session, user_id, channel_id, game_type):
        game_event = create_game_event(
            GameEventType.GAME_STARTED,
            user_id=user_id,
            channel_id=channel_id,
            game_type=game_type
        )
        print(f"=== {game_event} ===")