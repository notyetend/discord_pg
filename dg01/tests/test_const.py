import pytest

from dg01.const import create_game_event
from dg01.event_bus import EventBus,  GameEventType
from dg01.game_session import GameSession


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
    def game_session(self, user_id, channel_id, event_bus):
        return GameSession(user_id, channel_id, event_bus)

    @pytest.mark.asyncio
    async def test_create_game_event(self, game_session, user_id, channel_id):
        game_event = create_game_event(
            GameEventType.GAME_STARTED,
            user_id=user_id,
            channel_id=channel_id
        )
        print(f"=== {game_event} ===")

        game_event = create_game_event(
            GameEventType.GAME_ERROR,
            user_id=user_id,
            channel_id=channel_id,
            error_info="blabla",
            severity="hahaha"
        )
        print(f"=== {game_event} ===")