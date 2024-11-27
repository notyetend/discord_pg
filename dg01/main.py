import json
from pathlib import Path

import discord
from discord.ext import commands

from dg01.digimon_cog import GameCommandsCog
from dg01.errors import setup_logger
from dg01.game_manager import GameManager


logger = setup_logger(__name__)


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.game_manager = GameManager(self)
        self.data_manager = self.game_manager.data_manager
            
    async def setup_hook(self):
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
