from typing import Dict, List

from dg01.const import GameEventType, GameEventData, GameEvent

class EventBus:
    def __init__(self):
        # 이벤트 타입별 구독자(콜백 함수) 목록을 저장하는 딕셔너리
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: GameEventType, callback: callable):
        """
        특정 이벤트 타입에 대한 구독자(콜백 함수) 등록
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 발생 시 호출될 콜백 함수
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, game_event: GameEvent):
        """
        이벤트 발행 및 구독자들에게 통지
        
        Args:
            event_type: 발행할 이벤트 타입
            event_data: 이벤트와 함께 전달할 데이터
        """
        if game_event.type in self.subscribers:
            for callback in self.subscribers[game_event.type]:
                await callback(game_event.data)
