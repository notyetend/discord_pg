import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from dg01.games import GameType
from dg01.game_session import GameSession
from dg01.event_bus import EventBus
from dg01.const import GameState, create_game_event, GameEvent, GameEventData, GameEventType
from dg01.games.digimon.digimon_logic import DigimonLogic
from dg01.errors import GameError
from dg01.game_manager import GameManager


class TestGameManager:
    @pytest.fixture
    def user_id(self):
        return 111
    
    @pytest.fixture
    def channel_id(self):
        return 222

    @pytest.fixture
    def game_type(self):
        return GameType.DIGIMON

    """
    bot
        await send_game_message
        await add_cog
        await remove_cog

    session
        await cleanup
        await start_game

    channel
        await send
    
    """
    @pytest.fixture
    def session(self):
        session = MagicMock()
        session.cleanup = AsyncMock()
        session.start_game = AsyncMock()

    @pytest.fixture
    def bot(self):
        async def print_args(*args, **kwargs):
            print(f"\nsend() called with args: {args}")
            print(f"send() called with kwargs: {kwargs}")
            return MagicMock()  # 가짜 message 객체 반환
        
        message = MagicMock()
        message.id = MagicMock()
        message.id.return_value = "mock_message_id"

        channel = MagicMock()
        channel.send = AsyncMock(side_effect=print_args)
        channel.send.return_value = message

        bot = MagicMock()
        bot.get_channel = MagicMock()
        bot.get_channel.return_value = channel
        bot.send_game_message = AsyncMock()
        bot.send_game_message.return_value = message
        bot.add_cog = AsyncMock()
        bot.remove_cog = AsyncMock()
        return bot

    @pytest.fixture
    def game_manager(self, bot):
        return GameManager(bot)

    @pytest.mark.asyncio
    async def test_send_game_message(self, game_manager, channel_id):
        message = await game_manager.send_game_message(channel_id)
        print(f"=== {message} ===")

    @pytest.mark.asyncio
    async def test_create_game(self, game_manager, user_id, channel_id, game_type):
        session = await game_manager.create_game(user_id, channel_id, game_type)
        assert session.user_id == user_id
        assert session.channel_id == channel_id
        assert session.game_type == game_type

    @pytest.mark.asyncio
    async def test_end_game(self, game_manager, user_id, channel_id, game_type):
        session = await game_manager.create_game(user_id, channel_id, game_type)
        game_manager.sessions[(user_id, channel_id)] = session
        await game_manager.end_game(user_id, channel_id, game_type)

    @pytest.mark.asyncio
    async def test_handle_game_started(self, game_manager, user_id, channel_id, game_type):
        assert game_manager.handle_game_started in game_manager.event_bus.subscribers[GameEventType.GAME_STARTED]
        game_event = create_game_event(
            GameEventType.GAME_STARTED,
            user_id=user_id,
            channel_id=channel_id,
            game_type=game_type
        )
        await game_manager.handle_game_started(data=game_event.data)
        await game_manager.event_bus.publish(game_event=game_event)
        assert game_manager.bot.get_channel(game_event.data.channel_id).send.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_game_error(self, game_manager, user_id, channel_id, game_type):
        assert game_manager.handle_game_error in game_manager.event_bus.subscribers[GameEventType.GAME_ERROR]

        game_event = create_game_event(
            GameEventType.GAME_ERROR,
            user_id=user_id,
            channel_id=channel_id,
            error_info="test error message",
            severity="blabla"
        )
        await game_manager.handle_game_error(data=game_event.data)
        await game_manager.event_bus.publish(game_event=game_event)
        assert game_manager.bot.get_channel(game_event.data.channel_id).send.call_count == 2
