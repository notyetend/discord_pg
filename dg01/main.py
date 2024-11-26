import json
from pathlib import Path

import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.manager_game import GameManager
from dg01.games import GameType


logger = setup_logger(__name__)


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
    async def end_game(self, ctx: commands.Context, game_type_str: str):
        """게임 종료 명령어"""
        game_type = GameType(game_type_str.lower())
        success = await self.bot.game_manager.end_game(ctx.author.id, game_type)

        if success:
            await ctx.send(f"{game_type} 게임이 종료되었습니다.")
        else:
            await ctx.send("실행 중인 게임이 없습니다.")


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.game_manager = GameManager(self)
    
    async def setup_hook(self):
        print("GameBot.setup_hook called")
        await self.add_cog(GameCommandsCog(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')
            

if __name__ == "__main__":
    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()
    bot.run(token)
