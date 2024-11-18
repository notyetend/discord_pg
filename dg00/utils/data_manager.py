import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class DataManager:
    """게임 데이터를 관리하는 클래스"""
    
    DEFAULT_DATA = {
        "players": {}
    }
    
    def __init__(self, data_dir: str = 'data', filename: str = 'digimon_data.json'):
        """
        DataManager 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리 경로
            filename (str): 데이터 파일 이름
        """
        self.data_dir = Path(data_dir)
        self.filepath = self.data_dir / filename
        self._ensure_data_directory()
        
    def _ensure_data_directory(self) -> None:
        """데이터 디렉토리와 기본 파일이 존재하는지 확인하고 생성"""
        self.data_dir.mkdir(exist_ok=True)
        if not self.filepath.exists():
            self.save_data(self.DEFAULT_DATA)
            
    def load_data(self) -> Dict[str, Any]:
        """
        게임 데이터를 로드합니다.
        
        Returns:
            Dict[str, Any]: 로드된 게임 데이터
            
        Raises:
            json.JSONDecodeError: JSON 파일 형식이 잘못된 경우
        """
        try:
            if not self.filepath.exists():
                return self.DEFAULT_DATA
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict) or "players" not in data.keys():
                    return self.DEFAULT_DATA
                return data
        except json.JSONDecodeError as e:
            print(f"JSON file format is invalid: {e}")
            return self.DEFAULT_DATA
            
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        게임 데이터를 저장합니다.
        
        Args:
            data (Dict[str, Any]): 저장할 게임 데이터
            
        Returns:
            bool: 저장 성공 여부
            
        Raises:
            IOError: 파일 저장 중 오류 발생 시
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving data file: {e}")
            return False
            
    def get_player_data(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """
        특정 플레이어의 데이터를 조회합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 플레이어 데이터 또는 None
        """
        data = self.load_data()
        return data["players"].get(str(user_id))
        
    def update_player_data(self, user_id: str | int, updates: Dict[str, Any]) -> bool:
        """
        특정 플레이어의 데이터를 업데이트합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            updates (Dict[str, Any]): 업데이트할 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        data = self.load_data()
        str_user_id = str(user_id)
        
        if str_user_id not in data["players"]:
            return False
            
        data["players"][str_user_id].update(updates)
        return self.save_data(data)
        
    def create_player(self, user_id: str | int, initial_data: Dict[str, Any]) -> bool:
        """
        새로운 플레이어를 생성합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            initial_data (Dict[str, Any]): 초기 플레이어 데이터
            
        Returns:
            bool: 생성 성공 여부
        """
        data = self.load_data()
        str_user_id = str(user_id)
        
        if str_user_id in data["players"]:
            return False
        else:
            data["players"][str_user_id] = initial_data
            return self.save_data(data)
        
    def delete_player(self, user_id: str | int) -> bool:
        """
        플레이어 데이터를 삭제합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        data = self.load_data()
        str_user_id = str(user_id)
        
        if str_user_id not in data["players"]:
            return False
            
        del data["players"][str_user_id]
        return self.save_data(data)
        
    def backup_data(self, backup_filename: Optional[str] = None) -> bool:
        """
        현재 데이터를 백업합니다.
        
        Args:
            backup_filename (Optional[str]): 백업 파일 이름
            
        Returns:
            bool: 백업 성공 여부
        """
        if backup_filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"digimon_data_backup_{timestamp}.json"
            
        backup_path = self.data_dir / backup_filename
        
        try:
            data = self.load_data()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False