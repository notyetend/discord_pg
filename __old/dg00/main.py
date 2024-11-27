import discord
import sys

from dg00.config.config import GAME_CONFIG, ConfigLoader
from dg00.message.bot import DigimonDiscordBot


if __name__ == "__main__":
    try:
        TOKEN = ConfigLoader.load_token()
    except Exception as e:
        print(f"Error loading token: {str(e)}")
        sys.exit(1)

    try:
        bot = DigimonDiscordBot(GAME_CONFIG)
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Error: 디스코드 토큰이 올바르지 않습니다. token.json 파일을 확인해주세요.")
    except Exception as e:
        print(f"Error: 봇 실행 중 오류가 발생했습니다: {str(e)}")
