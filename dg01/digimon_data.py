from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, NamedTuple


@dataclass
class DigimonDataFields:
    """사용자 데이터 필드 정의"""
    user_id: int = field(default=-1, metadata={"primary_key": True, "type": "INTEGER", "default": -1})
    channel_id: int = field(default=-1, metadata={"type": "INTEGER", "nullable": False, "default": -1})
    stage_idx: int = field(default=0, metadata={"type": "INTEGER", "nullable": False, "default": 0})
    count: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    # data_absorbed: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    battles_won: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    battles_lost: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    last_cheer: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
    is_copying: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    evolution_started: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
    last_played: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})