import pytest
import asyncio
from datetime import datetime
from dg01.game_events import (
    EventType,
    EventBase,
    EventGameStarted,
    EventGameCleanup,
    EventError,
    EventUpdatePlayer,
    GameState
)

@pytest.fixture
def event_data():
    """기본 이벤트 데이터를 제공하는 fixture"""
    return {
        'user_id': 12345,
        'channel_id': 67890,
    }

@pytest.fixture
def sample_player_data():
    """샘플 플레이어 데이터를 제공하는 fixture"""
    return {
        'stage_idx': 1,
        'count': 100,
        'battles_won': 5,
        'battles_lost': 2
    }

def test_event_type_values():
    """EventType 열거형 값 테스트"""
    assert EventType.GAME_STARTED.value == "game_started"
    assert EventType.GAME_CLEANUP.value == "game_cleanup"
    assert EventType.GAME_ERROR.value == "game_error"
    assert EventType.UPDATE_PLAYER.value == "update_player"

def test_game_state_values():
    """GameState 열거형 값 테스트"""
    assert GameState.WAITING.value == "waiting"
    assert GameState.STARTING.value == "starting"
    assert GameState.PLAYING.value == "playing"
    assert GameState.PAUSED.value == "paused"
    assert GameState.FINISHED.value == "finished"
    assert GameState.CANCELLED.value == "cancelled"
    assert GameState.ERROR.value == "error"
    assert GameState.TIMEOUT.value == "timeout"

@pytest.mark.asyncio
async def test_event_base_creation(event_data):
    """EventBase 생성 및 기본 속성 테스트"""
    event = EventBase(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id'],
        event_type=EventType.GAME_STARTED
    )
    
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.event_type == EventType.GAME_STARTED
    assert event.created_at is not None
    assert isinstance(event.created_at, float)

@pytest.mark.asyncio
async def test_event_base_missing_event_type(event_data):
    """EventBase에서 event_type이 누락된 경우 테스트"""
    with pytest.raises(TypeError):
        EventBase(
            user_id=event_data['user_id'],
            channel_id=event_data['channel_id']
        )

@pytest.mark.asyncio
async def test_event_game_started(event_data):
    """EventGameStarted 이벤트 생성 테스트"""
    event = EventGameStarted(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id']
    )
    
    assert event.event_type == EventType.GAME_STARTED
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_event_game_cleanup(event_data):
    """EventGameCleanup 이벤트 생성 테스트"""
    event = EventGameCleanup(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id']
    )
    
    assert event.event_type == EventType.GAME_CLEANUP
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_event_error(event_data):
    """EventError 이벤트 생성 테스트"""
    error_info = "Test error message"
    severity = "HIGH"
    
    event = EventError(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id'],
        error_info=error_info,
        severity=severity
    )
    
    assert event.event_type == EventType.GAME_ERROR
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.error_info == error_info
    assert event.severity == severity
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_event_update_player(event_data, sample_player_data):
    """EventUpdatePlayer 이벤트 생성 테스트"""
    event = EventUpdatePlayer(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id'],
        player_data=sample_player_data
    )
    
    assert event.event_type == EventType.UPDATE_PLAYER
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.player_data == sample_player_data
    assert event.created_at is not None

def test_game_state_transitions():
    """GameState 상태 전이 가능성 테스트"""
    # 가능한 상태 전이 시나리오
    valid_transitions = [
        (GameState.WAITING, GameState.STARTING),
        (GameState.STARTING, GameState.PLAYING),
        (GameState.PLAYING, GameState.PAUSED),
        (GameState.PAUSED, GameState.PLAYING),
        (GameState.PLAYING, GameState.FINISHED),
        (GameState.PLAYING, GameState.CANCELLED),
        (GameState.PLAYING, GameState.ERROR),
        (GameState.PLAYING, GameState.TIMEOUT),
    ]
    
    for from_state, to_state in valid_transitions:
        assert isinstance(from_state, GameState)
        assert isinstance(to_state, GameState)
        assert from_state != to_state

@pytest.mark.asyncio
async def test_event_creation_time_ordering():
    """이벤트 생성 시간 순서 테스트"""
    events = []
    for _ in range(3):
        event = EventGameStarted(user_id=1, channel_id=1)
        events.append(event)
        await asyncio.sleep(0.01)  # 시간 차이를 만들기 위한 지연
    
    # 이벤트들이 생성된 순서대로 정렬되어 있는지 확인
    assert all(events[i].created_at < events[i+1].created_at 
              for i in range(len(events)-1))