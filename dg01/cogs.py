from discord.ext import commands

from dg01.states import GameType


class GameCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='시작')
    async def start_game(self, ctx: commands.Context, game_type_str: str):
        """게임 시작 명령어"""
        try:
            game_type = GameType(game_type_str.lower())
            success = await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, game_type)
            if success:
                await ctx.send(f"{game_type} 게임이 시작되었습니다!")
            else:
                await ctx.send("이미 게임이 실행 중입니다.")
        except ValueError:
            await ctx.send(f"지원하지 않는 게임 타입입니다. 지원 게임: {', '.join(type.value for type in GameType)}")

    @commands.command(name='종료')
    async def end_game(self, ctx: commands.Context):
        """게임 종료 명령어"""
        success = await self.bot.game_manager.end_game(ctx.channel.id)
        if success:
            await ctx.send("게임이 종료되었습니다.")
        else:
            await ctx.send("실행 중인 게임이 없습니다.")