import pytest
from unittest.mock import Mock, AsyncMock
from dg01.event_bus import EventBus
from dg01.game_events import (
    EventType,
    EventGameStarted,
    EventGameCleanup,
    EventError,
    EventUpdatePlayer
)

@pytest.fixture
def event_bus():
    """EventBus 인스턴스를 생성하는 fixture"""
    return EventBus()

@pytest.fixture
def sample_event_data():
    """테스트용 이벤트 데이터"""
    return {
        'user_id': 12345,
        'channel_id': 67890,
    }

@pytest.fixture
def mock_callback():
    """비동기 콜백 함수를 모방하는 fixture"""
    return AsyncMock()

@pytest.mark.asyncio
async def test_subscribe_single_callback(event_bus, mock_callback):
    """단일 콜백 구독 테스트"""
    event_bus.subscribe(EventType.GAME_STARTED, mock_callback)
    
    assert EventType.GAME_STARTED in event_bus.subscribers
    assert len(event_bus.subscribers[EventType.GAME_STARTED]) == 1
    assert event_bus.subscribers[EventType.GAME_STARTED][0] == mock_callback

@pytest.mark.asyncio
async def test_subscribe_multiple_callbacks(event_bus):
    """여러 콜백 구독 테스트"""
    callback1 = AsyncMock()
    callback2 = AsyncMock()
    callback3 = AsyncMock()
    
    event_bus.subscribe(EventType.GAME_STARTED, callback1)
    event_bus.subscribe(EventType.GAME_STARTED, callback2)
    event_bus.subscribe(EventType.GAME_STARTED, callback3)
    
    assert len(event_bus.subscribers[EventType.GAME_STARTED]) == 3
    assert callback1 in event_bus.subscribers[EventType.GAME_STARTED]
    assert callback2 in event_bus.subscribers[EventType.GAME_STARTED]
    assert callback3 in event_bus.subscribers[EventType.GAME_STARTED]

@pytest.mark.asyncio
async def test_subscribe_multiple_event_types(event_bus, mock_callback):
    """여러 이벤트 타입 구독 테스트"""
    event_bus.subscribe(EventType.GAME_STARTED, mock_callback)
    event_bus.subscribe(EventType.GAME_CLEANUP, mock_callback)
    event_bus.subscribe(EventType.GAME_ERROR, mock_callback)
    
    assert EventType.GAME_STARTED in event_bus.subscribers
    assert EventType.GAME_CLEANUP in event_bus.subscribers
    assert EventType.GAME_ERROR in event_bus.subscribers

@pytest.mark.asyncio
async def test_publish_event_with_single_subscriber(event_bus, sample_event_data, mock_callback):
    """단일 구독자에 대한 이벤트 발행 테스트"""
    event_bus.subscribe(EventType.GAME_STARTED, mock_callback)
    
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(event)
    
    mock_callback.assert_called_once_with(event)

@pytest.mark.asyncio
async def test_publish_event_with_multiple_subscribers(event_bus, sample_event_data):
    """여러 구독자에 대한 이벤트 발행 테스트"""
    callback1 = AsyncMock()
    callback2 = AsyncMock()
    
    event_bus.subscribe(EventType.GAME_STARTED, callback1)
    event_bus.subscribe(EventType.GAME_STARTED, callback2)
    
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(event)
    
    callback1.assert_called_once_with(event)
    callback2.assert_called_once_with(event)

@pytest.mark.asyncio
async def test_publish_event_no_subscribers(event_bus, sample_event_data):
    """구독자가 없는 이벤트 발행 테스트"""
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    # 구독자가 없는 경우에도 예외가 발생하지 않아야 함
    await event_bus.publish(event)

@pytest.mark.asyncio
async def test_publish_different_event_types(event_bus, sample_event_data):
    """여러 이벤트 타입 발행 테스트"""
    game_started_callback = AsyncMock()
    game_cleanup_callback = AsyncMock()
    
    event_bus.subscribe(EventType.GAME_STARTED, game_started_callback)
    event_bus.subscribe(EventType.GAME_CLEANUP, game_cleanup_callback)
    
    # GAME_STARTED 이벤트 발행
    start_event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(start_event)
    
    # GAME_CLEANUP 이벤트 발행
    cleanup_event = EventGameCleanup(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(cleanup_event)
    
    game_started_callback.assert_called_once_with(start_event)
    game_cleanup_callback.assert_called_once_with(cleanup_event)

@pytest.mark.asyncio
async def test_publish_error_event(event_bus, sample_event_data):
    """에러 이벤트 발행 테스트"""
    error_callback = AsyncMock()
    event_bus.subscribe(EventType.GAME_ERROR, error_callback)
    
    error_event = EventError(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id'],
        error_info="Test error",
        severity="HIGH"
    )
    await event_bus.publish(error_event)
    
    error_callback.assert_called_once_with(error_event)

@pytest.mark.asyncio
async def test_callback_exception_handling(event_bus, sample_event_data):
    """콜백 함수에서 예외 발생 시 처리 테스트"""
    async def failing_callback(event):
        raise Exception("Callback failed")
    
    event_bus.subscribe(EventType.GAME_STARTED, failing_callback)
    
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    
    # 콜백에서 예외가 발생해도 이벤트 발행은 계속되어야 함
    with pytest.raises(Exception, match="Callback failed"):
        await event_bus.publish(event)