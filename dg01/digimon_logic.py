import asyncio
from datetime import datetime, timezone

from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx
from dg01.errors import setup_logger
from dg01.game_events import EventType, EventUpdatePlayer

logger = setup_logger(__name__)


class DigimonLogic:
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass

    def update(self, player_data, delta_time):
        print(f"=== {delta_time:.3f} ===")
        print(f"====== {player_data=} ===============")

        updates = {}

        # check copy
        update_copy = self.copy_digimon(player_data=player_data, delta_time=delta_time)
        if update_copy:
            updates = {**updates, **update_copy}
        else:
            # stopped copying
            pass
        
        # check evolution
        update_evolution = self.check_evolution(player_data)
        if update_evolution:
            print(f"============ {update_evolution=} =============")
            updates = {**updates, **update_evolution}

        print(f"====== {updates=} ===============")
        if len(updates) > 0:
            update_player_event = EventUpdatePlayer(
                user_id=player_data['user_id']
                , channel_id=player_data['channel_id']
                , updates=updates
            )
            
            return [update_player_event]
        else:
            return []
        
    def copy_digimon(self, player_data, delta_time):
        if player_data["is_copying"] == 1:
            new_count = player_data["count"] + (STAGE_CONFIG[player_data["stage_idx"]]["copy_rate"] * delta_time)
            return {
                "count": int(new_count)
            }
        else:
            return None

    def check_evolution(self, player_data):
        stage_idx = player_data["stage_idx"]
        if stage_idx == max(STAGES.keys()):
            return False
        
        if player_data["count"] >= STAGE_CONFIG[stage_idx]["evolution_count"]:
            return {
                "stage_idx": get_next_stage_idx(stage_idx),
            }
        else:
            return False
        """
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
        """