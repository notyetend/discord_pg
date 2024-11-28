import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from dg01.game_session import GameSession
from dg01.event_bus import EventBus
from dg01.game_events import (
    GameState,
    EventType,
    EventGameStarted,
    EventError,
    EventGameCleanup
)
from dg01.errors import GameError
from dg01.data_manager import DataManager


@pytest.fixture
def event_bus():
    """이벤트 버스 fixture"""
    bus = EventBus()
    bus.publish = AsyncMock()
    return bus

@pytest.fixture
def game_session(event_bus):
    """게임 세션 fixture"""
    session = GameSession(
        user_id=12345,
        channel_id=67890,
        event_bus=event_bus,
        data_manager=DataManager()
    )
    session.data_manager.get_or_create_user_data = AsyncMock()
    session.data_manager.update_user_data = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_game_session_initialization(game_session):
    """게임 세션 초기화 테스트"""
    assert game_session.user_id == 12345
    assert game_session.channel_id == 67890
    assert game_session.state == GameState.WAITING
    assert game_session.tick_rate == 1.0
    assert game_session.message_id is None

@pytest.mark.asyncio
async def test_start_game(game_session):
    """게임 시작 테스트"""
    await game_session.start_game()
    
    assert game_session.state == GameState.PLAYING
    assert hasattr(game_session, 'last_update')
    assert hasattr(game_session, 'update_task')
    
    # GameStarted 이벤트가 발행되었는지 확인
    game_session.event_bus.publish.assert_called_once()
    event = game_session.event_bus.publish.call_args[0][0]
    assert isinstance(event, EventGameStarted)
    assert event.user_id == game_session.user_id
    assert event.channel_id == game_session.channel_id

@pytest.mark.asyncio
async def test_start_game_already_started(game_session):
    """이미 시작된 게임 시작 시도 테스트"""
    game_session.state = GameState.PLAYING
    
    with pytest.raises(GameError, match="Game already started"):
        await game_session.start_game()

@pytest.mark.asyncio
async def test_update_loop_basic_functionality(game_session):
    """업데이트 루프 기본 기능 테스트"""
    # 게임 로직 모의
    mock_events = [Mock(type=EventType.UPDATE_PLAYER, data={"user_id": 12345})]
    game_session.game_logic.update = Mock(return_value=mock_events)
    
    # 게임 시작
    await game_session.start_game()
    
    # 한 틱 실행
    await asyncio.sleep(1.1)
    
    # 업데이트가 실행되었는지 확인
    assert game_session.game_logic.update.called
    assert game_session.data_manager.get_or_create_user_data.called

    # 정리
    await game_session.cleanup()

@pytest.mark.asyncio
async def test_cleanup(game_session):
    """게임 세션 정리 테스트"""
    # 게임 시작
    await game_session.start_game()
    
    # 정리 실행
    await game_session.cleanup()
    
    assert game_session.state == GameState.FINISHED
    assert not game_session.update_task or game_session.update_task.done()
    
    # GameCleanup 이벤트가 발행되었는지 확인
    cleanup_event_call = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventGameCleanup)
    ]
    assert len(cleanup_event_call) == 1

@pytest.mark.asyncio
async def test_handle_error_game_error(game_session):
    """GameError 처리 테스트"""
    game_session.state = GameState.PLAYING
    error = GameError("Test game error")
    
    await game_session.handle_error(error)
    
    assert game_session.state == GameState.PAUSED
    
    # 에러 이벤트가 발행되었는지 확인
    error_event_call = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventError)
    ]
    assert len(error_event_call) == 1
    error_event = error_event_call[0][0][0]
    assert error_event.severity == 'error'

@pytest.mark.asyncio
async def test_handle_error_unknown_error(game_session):
    """알 수 없는 에러 처리 테스트"""
    game_session.state = GameState.PLAYING
    error = Exception("Unknown error")
    
    await game_session.handle_error(error)
    
    assert game_session.state == GameState.ERROR
    
    # 에러 이벤트가 발행되었는지 확인
    error_event_call = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventError)
    ]
    assert len(error_event_call) == 1
    error_event = error_event_call[0][0][0]
    assert error_event.severity == 'unknown'

@pytest.mark.asyncio
async def test_update_loop_error_handling(game_session):
    """업데이트 루프 에러 처리 테스트"""
    # 게임 로직이 예외를 발생시키도록 설정
    game_session.game_logic.update = Mock(side_effect=Exception("Test error"))
    
    # 게임 시작
    await game_session.start_game()
    
    # 에러가 발생할 때까지 대기
    await asyncio.sleep(1.1)
    
    # 게임이 에러 상태가 되었는지 확인
    assert game_session.state == GameState.ERROR
    
    # 에러 이벤트가 발행되었는지 확인
    error_event_calls = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventError)
    ]
    assert len(error_event_calls) > 0
