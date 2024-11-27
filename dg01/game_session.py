import asyncio
from typing import Optional

from discord.ext import commands

from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.event_bus import EventBus
from dg01.const import GameState, GameEventType, create_game_event
from dg01.data_manager import DataManager
from dg01.digimon_logic import DigimonLogic

logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, channel_id: int, event_bus: EventBus):
        self.user_id = user_id
        self.channel_id = channel_id
        self.event_bus = event_bus
        self.game_logic = DigimonLogic()
        self.data_manager = DataManager()
        self.state = GameState.WAITING
        self.tick_rate = 1.0
    
    async def start_game(self):
        if self.state != GameState.WAITING:
            raise GameError("Game already started")
        
        self.state = GameState.PLAYING
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        game_event = create_game_event(
            GameEventType.GAME_STARTED,
            user_id=self.user_id,
            channel_id=self.channel_id,
        )
        await self.event_bus.publish(game_event)

    async def update_loop(self):  # not used yet
        try:
            while self.state == GameState.PLAYING:
                current_time = asyncio.get_running_loop().time()
                delta_time = current_time - self.last_update
                
                # 게임 로직 업데이트
                events = self.game_logic.update(delta_time)
                for event in events:
                    await self.handle_event(event)
                
                # 게임 상태 표시 업데이트
                if self.message_id:
                    await self.update_game_display()
                
                self.last_update = current_time
                
                # 다음 틱까지 대기
                next_update = self.last_update + (1.0 / self.tick_rate)
                sleep_time = max(0, next_update - asyncio.get_running_loop().time())
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            await self.cleanup()
        except Exception as e:
            # raise e  # for test
            await self.handle_error(e)
    
    async def handle_event(self, event):
        print("handle_event called", event)

    async def update_game_display(self):
        print("update_game_display called")

    async def cleanup(self) -> None:
        """
        게임 세션의 리소스를 정리하고 종료합니다.
        - 실행 중인 태스크 취소
        - 이벤트 발행
        - 게임 상태 정리
        """
        try:
            # 업데이트 태스크 취소
            if hasattr(self, 'update_task') and self.update_task:
                self.update_task.cancel()
                self.update_task = None

            # 게임 종료 이벤트 발행
            # create_game_event(GameEventType.GAME_CLEANUP, self)  # @@@
            game_event = create_game_event(
                GameEventType.GAME_CLEANUP,
                user_id=self.user_id,
                channel_id=self.channel_id
            )
            await self.event_bus.publish(game_event)

            # 게임 상태를 FINISHED로 변경
            self.state = GameState.FINISHED

            logger.info(f"Cleaned up game session for user {self.user_id} and channel {self.channel_id}")

        except Exception as e:
            logger.error(f"Error during cleanup for user {self.user_id} and channel {self.channel_id}: {str(e)}")

    async def handle_error(self, error: Exception, ctx: Optional[commands.Context] = None) -> None:
        """
        게임 세션의 에러를 처리합니다.
        특정하지 못한 예외는 'unknown' 심각도로 처리하고 게임을 중단시킵니다.
        
        Args:
            error: 발생한 예외
            ctx: 디스코드 명령어 컨텍스트 (선택적)
        """
        try:
            # 에러 정보 구성
            error_info = {
                "user_id": str(self.user_id),
                "channel_id": str(self.channel_id),
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
            print(error_info)
            # 에러 심각도 결정
            if isinstance(error, GameCriticalError):
                severity = 'critical'
            elif isinstance(error, GameError):
                severity = 'error'
            elif isinstance(error, InvalidActionError):
                severity = 'warning'
            else:
                # 특정되지 않은 Exception
                severity = 'unknown'

            # 로깅
            if severity == 'unknown':
                logger.critical(f"Unknown Error in game session: {error_info}")
            elif severity == 'critical':
                logger.critical(f"Critical Error: {error_info}")
            elif severity == 'error':
                logger.error(f"Game Error: {error_info}")
            else:
                logger.warning(f"Warning: {error_info}")

            # 게임 상태 업데이트
            if severity in ['unknown', 'critical']:
                self.state = GameState.ERROR
                # 게임 강제 종료
                # await self.stop_game()
            elif severity == 'error' and self.state == GameState.PLAYING:
                self.state = GameState.PAUSED

            # 이벤트 발행
            game_event = create_game_event(
                GameEventType.GAME_ERROR,
                user_id=self.user_id,
                channel_id=self.channel_id,
                error_info=error_info,
                severity=severity
            )
            await self.event_bus.publish(game_event)
        except Exception as e:
            logger.critical(f"Error in error handler: {str(e)}")
            if ctx:
                try:
                    await ctx.send("An unexpected error occurred in the error handler.")
                except:
                    pass
