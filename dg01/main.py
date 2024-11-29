import json
from pathlib import Path


from dg01.game_bot import GameBot
from dg01.errors import setup_logger


logger = setup_logger(__name__)


if __name__ == "__main__":
    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()
    bot.run(token)
