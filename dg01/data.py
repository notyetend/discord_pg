import os
from pathlib import Path
from datetime import datetime, timezone
import json

from dg01.errors import setup_logger


logger = setup_logger(__name__)


class GameDataManager:
    def __init__(self, data_dir: str = './__game_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def get_user_data(self, user_id: int, channel_id: int) -> dict:
        """사용자의 게임 데이터를 불러옵니다."""
        default_data = {
            "stage": "디지타마",
            "count": 1,
            "data_absorbed": 0,
            "battles_won": 0,
            "battles_lost": 0,
            "last_cheer": None,
            "is_copying": True,
            "evolution_started": None,
            "channel_id": channel_id,
            "last_played": None
        }
        
        try:
            user_data_file = f"{self.data_dir}/user_{user_id}.json"
            if os.path.exists(user_data_file):
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(user_data_file, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=4)
                    return default_data
        except Exception as e:
            logger.error(f"데이터 로드 실패: {str(e)}")
            raise e
            return default_data
            
    def save_user_data(self, user_id: int, data: dict) -> bool:
        """사용자의 게임 데이터를 저장합니다."""
        try:
            user_data_file = f"{self.data_dir}/user_{user_id}.json"
            with open(user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"데이터 저장 실패: {str(e)}")
            return False
            
    def update_last_played(self, user_id: int) -> None:
        """사용자의 마지막 플레이 시간을 업데이트합니다."""
        data = self.get_user_data(user_id)
        data["last_played"] = datetime.now(timezone.utc).isoformat()
        self.save_user_data(user_id, data)