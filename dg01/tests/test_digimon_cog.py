import pytest
import discord
from unittest.mock import MagicMock, AsyncMock

from discord.ext import commands

from dg01.games.digimon.digimon_cog import DigimonCog


class MockBot(commands.Bot):
    """테스트용 Bot 클래스"""
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents)
        # self.user = MagicMock()
        # self.user.name = "TestBot"


@pytest.fixture
def bot():
    return MockBot()


@pytest.fixture
def ctx():
    ctx = MagicMock(spec=commands.Context)
    ctx.send = AsyncMock()
    return ctx

@pytest.fixture
def cog(bot):
    return DigimonCog(bot)

@pytest.mark.asyncio
async def test_start_command(cog, ctx):
    # given
    command = cog.start.callback

    # when
    await command(cog, ctx)
    
    # then
    ctx.send.assert_called_once_with('쓰담쓰담 쓰담쓰담')


@pytest.mark.asyncio
async def test_cheer_command(cog, ctx):
    # given
    command = cog.cheer.callback

    # when
    await command(cog, ctx)
    
    # then
    ctx.send.assert_called_once_with('응원 응원')


@pytest.mark.asyncio
async def test_cure_command(cog, ctx):
    # given
    command = cog.cure.callback

    # when
    await command(cog, ctx)
    
    # then
    ctx.send.assert_called_once_with('치료 치료')


# 에러 케이스 테스트 예시
@pytest.mark.asyncio
async def test_command_with_error(cog, ctx):
    # given
    command = cog.start.callback
    ctx.send.side_effect = Exception("Discord API Error")
    
    # when/then
    with pytest.raises(Exception):
        await command(cog, ctx)