from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import discord
from discord.ext import commands

from dg01.games.base import GameLogic
from dg01.errors import setup_logger, GameError
from dg01.games.digimon.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message


logger = setup_logger(__name__)


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ"])
    async def start(self, ctx: commands.Context):
         await ctx.send('쓰담쓰담 쓰담쓰담')

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')


class DigimonLogic(GameLogic):
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass
