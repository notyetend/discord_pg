from discord.ext import commands

from game_error import GameError


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    @commands.command()
    async def create(self, ctx):
        try:
            await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, "digimon")
        except GameError as e:
            await ctx.send(str(e))   
    """

    @commands.command(name="쓰담쓰담")
    async def start(self, ctx):
        try:
            await self.bot.game_manager.handle_command(ctx, "start")
            await ctx.send('쓰담쓰담 쓰담쓰담')
        except GameError as e:
            await ctx.send(str(e))   

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')


class GameLogic:
    def __init__(self):
        pass


class DigimonLogic(GameLogic):
    def __init__(self):
        pass

    def update(self, delta_time):
        events = []
        print(f"DigimonLogic update called - {delta_time=}")
        return events
