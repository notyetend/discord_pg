from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dg00.utils.data_manager import DataManager
from dg00.config.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message

class DigimonGame:
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self, data_manager: Optional[DataManager] = None):
        """
        DigimonGame 클래스 초기화
        
        Args:
            data_manager (Optional[DataManager]): 데이터 관리자 인스턴스
        """
        self.data_manager = data_manager or DataManager()
        self.data = self.data_manager.load_data()
    
    def get_default_player_data(self, channel_id):
        return {
            "stage": "디지타마",
            "count": 1,
            "data_absorbed": 0,
            "battles_won": 0,
            "battles_lost": 0,
            "last_cheer": None,
            "is_copying": True,
            "evolution_started": None,
            "channel_id": channel_id
        }
        
    def get_player_data(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """
        플레이어 데이터를 조회합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 플레이어 데이터 또는 None
        """
        return self.data_manager.get_player_data(user_id)
    
    def create_player(self, user_id: str | int, channel_id: id) -> Optional[Dict[str, Any]]:
        """
        새로운 플레이어를 생성합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 생성된 플레이어 데이터 또는 None (실패시)
        """
        if self.data_manager.create_player(user_id, self.get_default_player_data(channel_id)):
            self.data = self.data_manager.load_data()
            return self.data["players"].get(str(user_id))
        else:  # existing user
            return None
    
    def update_player(self, user_id: str | int, updates: Dict[str, Any]) -> bool:
        """
        플레이어 데이터를 업데이트합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            updates: 업데이트할 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if self.data_manager.update_player_data(user_id, updates):
            self.data = self.data_manager.load_data()
            return True
        return False

    def process_turn(self, user_id: str | int) -> Dict[str, Any]:
        """
        플레이어의 턴을 처리합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Dict[str, Any]: 턴 처리 결과
        """
        player_data = self.get_player_data(user_id)
        if not player_data or not player_data["is_copying"]:
            return {"status": "inactive"}

        stage_config = get_stage_config(player_data["stage"])
        if not stage_config:
            return {"status": "error", "message": "Invalid stage"}

        # 복제 및 데이터 흡수 계산
        new_count = int(player_data["count"] * (1 + stage_config["copy_rate"]))
        new_data = player_data["data_absorbed"] + stage_config["data_rate"]

        updates = {
            "count": new_count,
            "data_absorbed": new_data
        }

        # 랜덤 메시지 생성
        message = get_random_message(player_data["stage"])
        
        # 진화 체크
        evolution_status = self.check_evolution(player_data)
        if evolution_status:
            updates.update(evolution_status)

        self.update_player(user_id, updates)
        
        return {
            "status": "success",
            "count": new_count,
            "data_absorbed": new_data,
            "evolution": evolution_status,
            "message": message
        }

    def check_evolution(self, player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        진화 조건을 체크합니다.
        
        Args:
            player_data: 현재 플레이어 데이터
            
        Returns:
            Optional[Dict[str, Any]]: 진화 관련 업데이트 데이터 또는 None
        """
        if player_data["stage"] == "디아블로몬":
            return None

        stage_config = get_stage_config(player_data["stage"])
        if player_data["count"] >= stage_config["evolution_count"]:
            if player_data["evolution_started"] is None:
                return {
                    "evolution_started": datetime.now().isoformat()
                }
            
            evolution_time = datetime.fromisoformat(player_data["evolution_started"])
            time_passed = (datetime.now() - evolution_time).total_seconds()
            
            if time_passed >= stage_config["evolution_time"]:
                next_stage = get_next_stage(player_data["stage"])
                if next_stage:
                    return {
                        "stage": next_stage,
                        "count": 1,
                        "evolution_started": None
                    }
        return None

    def process_battle(self, user_id: str | int, battle_result: Dict[str, Any]) -> bool:
        """
        전투 결과를 처리합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            battle_result: 전투 결과 데이터
            
        Returns:
            bool: 처리 성공 여부
        """
        updates = {
            "count": battle_result["new_count"],
        }
        
        if battle_result["result"] == "win":
            updates["battles_won"] = self.data["players"][str(user_id)]["battles_won"] + 1
        else:
            updates["battles_lost"] = self.data["players"][str(user_id)]["battles_lost"] + 1
            updates["is_copying"] = False
            
        return self.update_player(user_id, updates)

    def apply_cheer(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """
        응원 효과를 적용합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 응원 적용 결과 또는 None
        """
        player_data = self.get_player_data(user_id)
        if not player_data:
            return None

        if not player_data["last_cheer"] or \
           datetime.now() - datetime.fromisoformat(player_data["last_cheer"]) >= timedelta(hours=1):
            self.update_player(user_id, {
                "last_cheer": datetime.now().isoformat()
            })
            return {"status": "success", "message": "응원 효과가 적용되었습니다!"}
            
        time_left = datetime.fromisoformat(player_data["last_cheer"]) + timedelta(hours=1) - datetime.now()
        return {
            "status": "cooldown",
            "message": f"다음 응원까지 {time_left.seconds // 60}분 남았습니다."
        }

    def reset_player(self, user_id: str | int) -> bool:
        """
        플레이어 데이터를 초기화합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            bool: 초기화 성공 여부
        """
        if self.data_manager.delete_player(user_id):
            return bool(self.create_player(user_id))
        return False
    
    def get_stage_config(self, stage):
        return get_stage_config(stage)