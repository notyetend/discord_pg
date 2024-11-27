import asyncio
from datetime import datetime, timezone

from dg01.digimon_config import STAGES, STAGE_CONFIG
from dg01.errors import setup_logger


logger = setup_logger(__name__)


class DigimonLogic:
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass

    def check_evolution(self, player_data):
        stage_idx = player_data["stage_idx"]
        if stage_idx == max(STAGES.keys()):
            return None
        
        if player_data["count"] >= STAGE_CONFIG[stage_idx]["evolution_count"]:
            if player_data["evolution_started"] is None:  # 진화 시작 전
                return {"evolution_started": datetime.now(timezone.utc).isoformat()}
            else:
                evolution_time = datetime.fromisoformat(player_data["evolution_started"])
                time_passed = (datetime.now(timezone.utc) - evolution_time).total_seconds()
            
                if time_passed >= STAGE_CONFIG[stage_idx]["evolution_time"]:
                    return {
                        "status": "evolved",
                        "new_stage_idx": sorted(STAGES.keys())[stage_idx + 1]
                    }
        else:
            return None
                    