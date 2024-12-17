import json
import argparse
from pathlib import Path

import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.game_manager import GameManager
from digimon_config import update_digimon_config_csv

logger = setup_logger(__name__)


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.game_manager = GameManager(self)

    async def setup_hook(self):
        await self.add_cog(self.game_manager)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')

    async def on_message(self, message):
        if message.author.bot:
            return

        # await self.game_manager.handle_quiz_message(message)
        await self.process_commands(message)


def parse_args():
    parser = argparse.ArgumentParser(description='Digimon Game Bot')
    parser.add_argument('--update_config', action='store_true',
                       help='Update digimon config from Google Sheets')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    if args.update_config:
        logger.info("Updating digimon config from Google Sheets...")
        try:
            update_digimon_config_csv()
        except Exception as e:
            logger.info("Config update failed with", e)
        else:
            logger.info("Config update completed")

    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()

    """
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        
        await bot.game_manager.handle_quiz_message(message)
        await bot.process_commands(message)
    """
    bot.run(token)
