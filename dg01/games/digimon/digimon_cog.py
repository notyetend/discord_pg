from discord.ext import commands

from dg01.errors import setup_logger

logger = setup_logger(__name__)


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ"])
    async def start(self, ctx: commands.Context):
        await ctx.send('쓰담쓰담 쓰담쓰담')

    @commands.command(name="현황")
    async def cheer(self, ctx):
        await ctx.send('현황 현황')

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')
