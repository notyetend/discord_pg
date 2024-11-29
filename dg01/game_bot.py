from dg01.game_cog import GameCommandsCog
from dg01.game_manager import GameManager


import discord
from discord.ext import commands


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.game_manager = GameManager(self)
        self.cog = GameCommandsCog(self)

    async def setup_hook(self):
        await self.add_cog(self.cog)
        # await self.game_manager.restore_sessions()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')