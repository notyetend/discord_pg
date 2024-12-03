from dataclasses import field
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Type
from abc import ABC
from typing import TypeVar, Generic


class GameState(Enum):
    """
    게임의 가능한 모든 상태를 정의하는 열거형 클래스
    """
    WAITING = "waiting"          # 게임 생성 후 시작 대기 중
    STARTING = "starting"        # 게임 시작 프로세스 진행 중
    PLAYING = "playing"         # 게임 진행 중
    PAUSED = "paused"          # 게임 일시 중지
    FINISHED = "finished"       # 게임 정상 종료
    CANCELLED = "cancelled"     # 게임 중도 취소
    ERROR = "error"            # 게임 오류 상태
    TIMEOUT = "timeout"        # 시간 초과로 인한 종료


class EventType(Enum):
    GAME_STARTED = "game_started"
    GAME_CLEANUP = "game_cleanup"
    GAME_ERROR = "game_error"
    CREATE_PLAYER = "create_player"
    UPDATE_PLAYER = "update_player"
    QUIZ_PASS_NEEDED = "quiz_pass_needed"
    BATTLE_WIN = "battle_win"
    BATTLE_LOSE = "battle_lose"
    BATTLE_ITEM_GET = "battle_item_get"
    UPDATE_DASHBOARD = "update_dashboard"
    EVOLVED = "evolved"

@dataclass
class EventBase:
    user_id: int
    channel_id: int
    event_type: EventType
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = asyncio.get_running_loop().time()
        
        assert self.event_type is not None

@dataclass
class EventGameStarted(EventBase):
    event_type: EventType = EventType.GAME_STARTED

@dataclass
class EventGameCleanup(EventBase):
    event_type: EventType = EventType.GAME_CLEANUP

@dataclass
class EventError(EventBase):
    error_info: str = ""
    severity: str = ""
    event_type: EventType = EventType.GAME_ERROR

@dataclass
class EventUpdatePlayer(EventBase):
    updates: dict = field(default_factory=dict)
    event_type: EventType = EventType.UPDATE_PLAYER

@dataclass
class EventQuizPassNeeded(EventBase):
    quiz_question: str = ""
    quiz_answer: str = ""
    event_type: EventType = EventType.QUIZ_PASS_NEEDED

@dataclass
class EventBattleWin(EventBase):
    event_type: EventType = EventType.BATTLE_WIN

@dataclass
class EventBattleLose(EventBase):
    count_lost: int = 0  # 전투 패비로 잃게된 개체수
    event_type: EventType = EventType.BATTLE_LOSE

@dataclass
class EventBattleItemGet(EventBase):
    obtained_item_id: int = -1  # 전투 승리 후 확률적으로 얻게된 아이템의 식별자
    event_type: EventType = EventType.BATTLE_ITEM_GET

@dataclass
class EventUpdateDashboard(EventBase):
    event_type: EventType =  EventType.UPDATE_DASHBOARD

@dataclass
class EventEvolved(EventBase):
    event_type: EventType = EventType.EVOLVED