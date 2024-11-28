from dataclasses import field
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Type
from abc import ABC
from typing import TypeVar, Generic


class EventType(Enum):
    GAME_STARTED = "game_started"
    GAME_CLEANUP = "game_cleanup"
    GAME_ERROR = "game_error"
    CREATE_PLAYER = "create_player"
    UPDATE_PLAYER = "update_player"


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
