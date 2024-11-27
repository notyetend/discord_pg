import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Type
from abc import ABC
from typing import TypeVar, Generic


class GameEventType(Enum):
    GAME_STARTED = "game_started"
    GAME_CLEANUP = "game_cleanup"
    GAME_ERROR = "game_error"


class GameEventData(ABC):
    pass


T = TypeVar('T', bound=GameEventData)

@dataclass
class GameEvent(Generic[T]):
    """게임 관련 이벤트를 나타내는 제네릭 클래스입니다.

    타입 파라미터 T는 EventData를 상속받은 클래스만 허용되며,
    각 이벤트 타입에 맞는 데이터 클래스를 지정해야 합니다.

    Attributes:
        type (EventType): 이벤트의 종류 (예: GAME_STARTED, GAME_ENDED)
        data (T): 이벤트와 관련된 데이터. T는 EventData의 하위 클래스
        created_at (float): 이벤트 생성 시각 (Unix timestamp)
            None으로 전달 시 자동으로 현재 시각이 설정됨

    Type Parameters:
        T: EventData를 상속받은 클래스 (예: GameEventDefaultData, GameEndedData)
            이벤트 타입에 맞는 데이터 클래스를 지정해야 함

    Examples:
        >>> data = GameEventDefaultData(user_id="123", channel_id="456")
        >>> event = GameEvent[GameEventDefaultData](
        ...     type=EventType.GAME_STARTED,
        ...     data=data
        ... )

    Note:
        created_at이 None으로 전달되면 __post_init__에서 자동으로 현재 시각이 설정됩니다.
    """
    type: GameEventType
    data: T    # 특정 EventData 타입만 허용
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = asyncio.get_running_loop().time()


@dataclass
class GameEventDefaultData(GameEventData):
    user_id: str
    channel_id: str
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = asyncio.get_running_loop().time()


@dataclass
class GameEventErrorData(GameEventData):
    user_id: str
    channel_id: str
    error_info: str
    severity: str
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = asyncio.get_running_loop().time()


EVENT_DATA_MAPPING: Dict[GameEventType, Type[GameEventData]] = {
    GameEventType.GAME_STARTED: GameEventDefaultData,
    GameEventType.GAME_CLEANUP: GameEventDefaultData,
    GameEventType.GAME_ERROR: GameEventErrorData,
    # EventType.GAME_ENDED: GameEndedData,
    # EventType.PLAYER_MOVED: PlayerMovedData,
}


# 이벤트 생성 헬퍼 함수
def create_game_event(event_type: GameEventType, **data) -> GameEvent:
    """각 이벤트 타입에 맞는 GameEvent 객체를 생성합니다.

    Args:
        event_type (EventType): 생성할 이벤트의 타입 (예: EventType.GAME_STARTED)
        **data: 이벤트 데이터 필드들. 각 이벤트 타입에 맞는 필드들을 키워드 인자로 전달
            - GAME_STARTED: user_id, channel_id
            - GAME_ENDED: winner_id, score
            - PLAYER_MOVED: player_id, move, position
            
    Returns:
        GameEvent: 생성된 이벤트 객체
        
    Raises:
        KeyError: 주어진 event_type이 EVENT_DATA_MAPPING에 없는 경우
        TypeError: data의 필드가 해당 EventData 클래스의 필드와 일치하지 않는 경우
        
    Examples:
        >>> event = create_game_event(
        ...     EventType.GAME_STARTED,
        ...     user_id="123",
        ...     channel_id="456",
        ... )
        >>> isinstance(event.data, GameEventDefaultData)
        True

    Note:
        이 함수는 비동기 함수내에서만 호출해야한다.(created_at 세팅 때문)
    """
    data_class = EVENT_DATA_MAPPING[event_type]
    event_data = data_class(**data)
    return GameEvent[data_class](type=event_type, data=event_data)


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

