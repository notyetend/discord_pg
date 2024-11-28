import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from discord.ext import commands
from dg01.digimon_cog import GameCommandsCog
from dg01.errors import GameError
from dg01.digimon_config import STAGES
from dg01.game_events import EventType

@pytest.fixture
def mock_bot():
    """Mock discord bot fixture"""
    bot = Mock(spec=commands.Bot)
    bot.game_manager = AsyncMock()
    bot.game_manager.data_manager = AsyncMock()
    bot.game_manager.data_manager.get_or_create_user_data = AsyncMock()
    bot.game_manager.data_manager.get_or_create_user_data.return_value = {
        "user_id": 123,
        "stage_idx": 1,
        "count": 100,
        "battles_won": 5,
        "battles_lost": 2,
        "is_copying": True
    }
    return bot

@pytest.fixture
def mock_context():
    """Mock discord context fixture"""
    ctx = Mock(spec=commands.Context)
    ctx.author = Mock(spec=discord.Member)
    ctx.author.id = 12345
    ctx.author.name = "TestUser"
    ctx.channel = Mock(spec=discord.TextChannel)
    ctx.channel.id = 67890
    ctx.send = AsyncMock()
    return ctx

@pytest.fixture
def cog(mock_bot):
    """GameCommandsCog fixture"""
    return GameCommandsCog(mock_bot)

@pytest.mark.asyncio
async def test_start_command_success(cog, mock_context):
    """디지스타트 명령어 성공 테스트"""
    # 게임 매니저가 성공을 반환하도록 설정
    cog.bot.game_manager.start_session.return_value = EventType.CREATE_PLAYER
    
    # 명령어 직접 호출
    command = cog.start.callback
    await command(cog, mock_context)
    
    # 게임 매니저 호출 확인
    cog.bot.game_manager.start_session.assert_called_once_with(
        mock_context.author.id,
        mock_context.channel.id
    )
    
    # 성공 메시지 확인
    mock_context.send.assert_called_once()
    assert "짜잔!" in mock_context.send.call_args[0][0]
    assert mock_context.author.name in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_start_command_already_exists(cog, mock_context):
    """이미 존재하는 게임 시작 시도 테스트"""
    cog.bot.game_manager.start_session.return_value = EventType.GAME_STARTED
    
    command = cog.start.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "이미" in mock_context.send.call_args[0][0]
    assert mock_context.author.name in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_first_evolve_success(cog, mock_context):
    """쓰담쓰담 명령어 성공 테스트"""
    # 초기 스테이지 데이터 설정
    initial_data = {
        "stage_idx": min(STAGES.keys()),
        "count": 1,
        "battles_won": 0,
        "battles_lost": 0
    }
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = initial_data
    cog.bot.game_manager.data_manager.update_user_data.return_value = True
    
    command = cog.first_evolve.callback
    await command(cog, mock_context)
    
    # 데이터 업데이트 확인
    cog.bot.game_manager.data_manager.update_user_data.assert_called_once()
    updated_data = cog.bot.game_manager.data_manager.update_user_data.call_args[0][1]
    assert updated_data["stage_idx"] == min(STAGES.keys()) + 1
    
    # 성공 메시지 확인
    mock_context.send.assert_called_once()
    assert "부화했습니다" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_first_evolve_already_evolved(cog, mock_context):
    """이미 진화한 상태에서 쓰담쓰담 시도 테스트"""
    player_data = {
        "stage_idx": min(STAGES.keys()) + 1,
    }
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = player_data
    
    command = cog.first_evolve.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "이미 부화했어" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_status_command_with_game(cog, mock_context):
    """현황 명령어 테스트 (게임 존재)"""
    player_data = {
        "stage_idx": 1,
        "count": 100,
        "battles_won": 5,
        "battles_lost": 2,
        "is_copying": True
    }
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = player_data
    
    command = cog.status.callback
    await command(cog, mock_context)
    
    # embed로 응답했는지 확인
    mock_context.send.assert_called_once()
    call_kwargs = mock_context.send.call_args[1]
    assert 'embed' in call_kwargs
    
    # embed 내용 확인
    embed = call_kwargs['embed']
    assert isinstance(embed, discord.Embed)
    assert str(player_data['count']) in embed.fields[0].value
    assert str(player_data['battles_won']) in embed.fields[0].value
    assert str(player_data['battles_lost']) in embed.fields[0].value

@pytest.mark.asyncio
async def test_status_command_no_game(cog, mock_context):
    """현황 명령어 테스트 (게임 없음)"""
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = None
    
    command = cog.status.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "아직 게임을 시작하지 않았습니다" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_end_game_success(cog, mock_context):
    """방생 명령어 성공 테스트"""
    cog.bot.game_manager.end_game.return_value = True
    
    command = cog.end_game.callback
    await command(cog, mock_context)
    
    # 게임 매니저 호출 확인
    cog.bot.game_manager.end_game.assert_called_once_with(
        mock_context.author.id,
        mock_context.channel.id
    )
    
    # 성공 메시지 확인
    mock_context.send.assert_called_once()
    assert "작별" in mock_context.send.call_args[0][0]
    assert mock_context.author.name in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_end_game_no_game(cog, mock_context):
    """게임이 없는 상태에서 방생 시도 테스트"""
    cog.bot.game_manager.end_game.return_value = False
    
    command = cog.end_game.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "아직 네 디지몬이 없는데" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_command_error_handling(cog, mock_context):
    """명령어 에러 처리 테스트"""
    cog.bot.game_manager.start_session.side_effect = ValueError()
    
    command = cog.start.callback
    with pytest.raises(GameError):
        await command(cog, mock_context)