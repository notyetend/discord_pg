import pytest
import asyncio

from dg01.events import EventBus, GameEventType
from dg01.const import create_game_event, GameType


class TestEventBus:
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
    def event_bus(self):
        return EventBus()
    
    @pytest.fixture
    def test_callback(self):
        async def test_callback(x):
            await asyncio.sleep(1)
            print("callback called", f"{x}_output2")
        return test_callback

    @pytest.mark.asyncio
    async def test_subscribe(self, event_bus, test_callback, user_id, channel_id, game_type):
        game_event = create_game_event(
            GameEventType.GAME_STARTED,
            user_id=user_id,
            channel_id=channel_id,
            game_type=game_type
        )
        event_bus.subscribe(game_event.type, test_callback)

        assert test_callback in event_bus.subscribers[game_event.type]
    
    @pytest.mark.asyncio
    async def test_publish(self, event_bus, test_callback, user_id, channel_id, game_type, capsys):
        game_event = create_game_event(
            GameEventType.GAME_STARTED,
            user_id=user_id,
            channel_id=channel_id,
            game_type=game_type
        )
        event_bus.subscribe(game_event.type, test_callback)

        await event_bus.publish(game_event)
        captured = capsys.readouterr()  # 출력물을 캡쳐한다.
        assert captured.out == f"callback called {game_event.data.__repr__()}_output2\n"