import json
from pathlib import Path
from dg00.config.config import GAME_CONFIG


class ConfigLoader:
    @staticmethod
    def load_token() -> str:
        """Discord 봇 토큰을 로드합니다."""
        try:
            with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'discord_token' not in data:
                    raise KeyError("token.json 파일에 'discord_token' 키가 없습니다.")
                return data['discord_token']
        except FileNotFoundError:
            raise FileNotFoundError(
                "token.json 파일을 찾을 수 없습니다.\n"
                "config/token.json 파일을 다음과 같이 생성해주세요:\n"
                '{\n    "discord_token": "YOUR_BOT_TOKEN"\n}'
            )
        except json.JSONDecodeError:
            raise ValueError("token.json 파일의 JSON 형식이 올바르지 않습니다.")

    @staticmethod
    def get_config() -> dict:
        """게임 설정을 반환합니다."""
        return GAME_CONFIG

    @staticmethod
    def get_stage_config(stage: str) -> dict:
        """특정 스테이지의 설정을 반환합니다."""
        return GAME_CONFIG['stages'].get(stage)

    @staticmethod
    def get_battle_settings() -> dict:
        """전투 관련 설정을 반환합니다."""
        return GAME_CONFIG['battle_settings']

    @staticmethod
    def get_events_config() -> dict:
        """이벤트 관련 설정을 반환합니다."""
        return GAME_CONFIG['events']
    