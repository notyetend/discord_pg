import pytest
import asyncio
from unittest.mock import MagicMock

from dg01.game_session import GameSession
from dg01.event_bus import EventBus
from dg01.const import GameState, create_game_event, GameEvent, GameEventData, GameEventType
from dg01.errors import GameError
from dg01.digimon_logic import DigimonLogic


class TestGameSession:
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
        game_session = GameSession(user_id, channel_id, event_bus)
        game_session.game_logic = MagicMock()
        game_session.game_logic.update.return_value = ['=== dummy_event ===']
        game_session.tick_rate = 10
        game_session.message_id = None
        return game_session
    
    def test_create_game_logic(self, game_session):
        assert isinstance(game_session.game_logic, DigimonLogic)

    @pytest.mark.asyncio
    async def test_start_game__case_error(self, game_session):
        game_session.state = GameState.STARTING
        with pytest.raises(GameError) as exc_info:
            await game_session.start_game()

        # assert str(exc_info.value) == "Game already started"

    @pytest.mark.asyncio
    async def test_start_game__case_normal(self, user_id, channel_id, game_session, event_bus, capsys):
        test_callback_output = "=== Callback called - {callback_arg} ==="
        async def test_callback(callback_arg):
            await asyncio.sleep(1)
            print(test_callback_output.format(callback_arg=callback_arg))
            
        assert game_session.state == GameState.WAITING

        game_event = create_game_event(
            event_type=GameEventType.GAME_STARTED,
            user_id=user_id,
            channel_id=channel_id
        )
        event_bus.subscribe(game_event.type, test_callback)
        await game_session.start_game()

        assert game_session.game_logic.update.called
        print(f"\n=== {game_session.game_logic.update.call_count=} ===")

        # captured = capsys.readouterr()  # 출력물을 캡쳐한다.
        # assert captured.out[:-1] == test_callback_output.format(callback_arg=game_event.data.__repr__())
        # captured.out의 마지막에 \n 이 자동추가되어 제거

    @pytest.mark.asyncio
    async def test_update_loop__case_cancelled(self, game_session):
        game_session.state = GameState.CANCELLED
        await game_session.update_loop()

    @pytest.mark.asyncio
    async def test_update_loop__case_playing(self, game_session):
        assert game_session.state == GameState.WAITING

        # start_game을 통해 게임 시작
        await game_session.start_game()

        # 3초 후에 게임 상태를 FINISHED로 변경하는 태스크 생성
        async def change_state_after_delay():
            await asyncio.sleep(0.3)
            game_session.state = GameState.FINISHED

        await change_state_after_delay()

        assert game_session.game_logic.update.called
        print(f"\n=== {game_session.game_logic.update.call_count=} ===")
        assert game_session.state == GameState.FINISHED

    @pytest.mark.asyncio
    async def test_update_loop__case_error(self, game_session):
        """
        에러가 발생하면 state값이 ERROR로 바뀌면서
        while self.state == GameState.PLAYING: 때문에 루프를 나가게 된다.
        """
        game_session.game_logic = MagicMock()
        game_session.game_logic.update.side_effect = Exception("Error")
        game_session.tick_rate = 10
        game_session.message_id = None

        # start_game을 통해 게임 시작
        await game_session.start_game()

        # 3초 후에 게임 상태를 FINISHED로 변경하는 태스크 생성
        async def change_state_after_delay():
            await asyncio.sleep(0.3)
            game_session.state = GameState.FINISHED

        await change_state_after_delay()

        assert game_session.game_logic.update.called
        print(f"\n=== {game_session.game_logic.update.call_count=} ===")
        assert game_session.state == GameState.FINISHED

    @pytest.mark.asyncio
    async def test_cleanup(self, game_session):
        assert game_session.state == GameState.WAITING
        game_session.game_logic = MagicMock()
        game_session.game_logic.update.return_value = ['=== dummy_event ===']
        game_session.tick_rate = 10
        game_session.message_id = None

        # start_game을 통해 게임 시작
        await game_session.start_game()

        