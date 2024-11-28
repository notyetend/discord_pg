import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from discord.ext import commands
from dg01.game_manager import GameManager
from dg01.game_events import EventType, EventGameStarted, EventError
from dg01.errors import GameError

@pytest.fixture
def mock_bot():
    """Mock discord bot fixture"""
    bot = Mock(spec=commands.Bot)
    bot.get_channel = Mock()
    bot.game_manager = Mock()
    bot.game_manager.data_manager = Mock()
    return bot

@pytest.fixture
def mock_channel():
    """Mock discord channel fixture"""
    channel = AsyncMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    return channel

@pytest.fixture
def game_manager(mock_bot):
    """GameManager fixture"""
    return GameManager(mock_bot)

@pytest.mark.asyncio
async def test_start_session(game_manager):
    """게임 생성 테스트"""
    user_id = 12345
    channel_id = 67890
    
    # 새 게임 생성
    result = await game_manager.start_session(user_id, channel_id)
    assert result == EventType.GAME_STARTED
    assert user_id in game_manager.sessions
    assert game_manager.sessions[user_id].user_id == user_id
    assert game_manager.sessions[user_id].channel_id == channel_id
    
    # 중복 생성 시도
    result = await game_manager.start_session(user_id, channel_id)
    assert result is EventType.GAME_STARTED

@pytest.mark.asyncio
async def test_end_game(game_manager):
    """게임 종료 테스트"""
    # 게임 생성
    user_id = 12345
    channel_id = 67890
    await game_manager.start_session(user_id, channel_id)
    
    # 게임 종료
    result = await game_manager.end_session(user_id)
    assert result is True
    assert user_id not in game_manager.sessions
    
    # 존재하지 않는 게임 종료 시도
    result = await game_manager.end_session(99999)
    assert result is False

@pytest.mark.asyncio
async def test_handle_game_started(game_manager, mock_channel):
    """게임 시작 이벤트 처리 테스트"""
    channel_id = 67890
    user_id = 12345
    
    # 채널 mock 설정
    game_manager.bot.get_channel.return_value = mock_channel
    
    # 게임 시작 이벤트 생성
    event = EventGameStarted(
        user_id=user_id,
        channel_id=channel_id
    )
    
    # 이벤트 처리
    await game_manager.handle_game_started(event)
    
    # 채널 메시지 전송 확인
    mock_channel.send.assert_called_once()
    assert str(user_id) in mock_channel.send.call_args[0][0]
    assert str(channel_id) in mock_channel.send.call_args[0][0]

@pytest.mark.asyncio

@pytest.mark.asyncio
async def test_handle_game_error(game_manager, mock_channel):
    """게임 에러 이벤트 처리 테스트"""
    channel_id = 67890
    error_info = "Test error message"
    
    # 채널 mock 설정
    game_manager.bot.get_channel.return_value = mock_channel
    
    # 에러 이벤트 생성
    event = EventError(
        user_id=12345,
        channel_id=channel_id,
        error_info=error_info,
        severity="HIGH"
    )
    
    # 이벤트 처리
    await game_manager.handle_game_error(event)
    
    # 에러 메시지 전송 확인
    mock_channel.send.assert_called_once()
    assert error_info in mock_channel.send.call_args[0][0]

@pytest.mark.asyncio
async def test_send_game_message(game_manager, mock_channel):
    """게임 메시지 전송 테스트"""
    channel_id = 67890
    
    # 채널 mock 설정
    game_manager.bot.get_channel.return_value = mock_channel
    mock_message = Mock(spec=discord.Message)
    mock_channel.send.return_value = mock_message
    
    # 메시지 전송
    result = await game_manager.send_game_message(channel_id)
    
    # 결과 확인
    mock_channel.send.assert_called_once()
    assert isinstance(mock_channel.send.call_args[1]['embed'], discord.Embed)
    assert result == mock_message

@pytest.mark.asyncio
async def test_send_game_message_no_channel(game_manager):
    """채널이 없는 경우의 게임 메시지 전송 테스트"""
    channel_id = 67890
    game_manager.bot.get_channel.return_value = None
    
    with pytest.raises(GameError, match=f"Cannot find channel with ID {channel_id}"):
        await game_manager.send_game_message(channel_id)

@pytest.mark.asyncio
async def test_send_game_message_forbidden(game_manager, mock_channel):
    """권한이 없는 경우의 게임 메시지 전송 테스트"""
    channel_id = 67890
    game_manager.bot.get_channel.return_value = mock_channel
    mock_channel.send.side_effect = discord.Forbidden(Mock(), "No permission")
    
    with pytest.raises(GameError, match="Bot doesn't have permission"):
        await game_manager.send_game_message(channel_id)

@pytest.mark.asyncio
async def test_event_subscription(game_manager):
    """이벤트 구독 테스트"""
    assert EventType.GAME_STARTED in game_manager.event_bus.subscribers
    assert EventType.GAME_ERROR in game_manager.event_bus.subscribers
    assert game_manager.handle_game_started in game_manager.event_bus.subscribers[EventType.GAME_STARTED]
    assert game_manager.handle_game_error in game_manager.event_bus.subscribers[EventType.GAME_ERROR]

def test_multiple_game_sessions(game_manager):
    """여러 게임 세션 관리 테스트"""
    sessions_data = [
        (12345, 67890),
        (23456, 78901),
        (34567, 89012)
    ]
    
    async def create_sessions():
        for user_id, channel_id in sessions_data:
            result = await game_manager.start_session(user_id, channel_id)
            assert result in [EventType.GAME_STARTED, EventType.CREATE_PLAYER]
    
    # 여러 세션 생성
    asyncio.run(create_sessions())
    
    # 세션 수 확인
    assert len(game_manager.sessions) == len(sessions_data)
    
    # 각 세션 정보 확인
    for user_id, channel_id in sessions_data:
        assert user_id in game_manager.sessions
        assert game_manager.sessions[user_id].channel_id == channel_id