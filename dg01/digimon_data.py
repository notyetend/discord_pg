from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, NamedTuple


@dataclass
class DigimonDataFields:
    """사용자 데이터 필드 정의"""
    user_id: int = field(default=-1, metadata={"primary_key": True, "type": "INTEGER", "default": -1})
    channel_id: int = field(default=-1, metadata={"type": "INTEGER", "nullable": False, "default": -1})
    stage_idx: int = field(default=0, metadata={"type": "INTEGER", "nullable": False, "default": 0})
    count: int = field(default=0, metadata={"type": "INTEGER", "default": 0})  # 진화 요건이 충족되었으나, 퀴즈 풀이가 필요한 상황
    quiz_pass_needed: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    quiz_question: str = field(default="", metadata={"type": "TEXT", "nullable": False, "default": ""})
    quiz_answer: str = field(default="", metadata={"type": "TEXT", "nullable": False, "default": ""})
    quiz_published: int = field(default=0, metadata={"type": "INTEGER", "default": 0})  # 퀴즈를 출제했음. 정해진 시간내에 답을 하지 않으면 이 값을 0으로 만들고 퀴즈를 다시 출제
    battles_won: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    battles_lost: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    last_cheer: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
    is_copying: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    last_played: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})