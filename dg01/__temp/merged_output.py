from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from dg01.const import GameType
from dg01.const import GameType, GameState
from dg01.errors import GameError
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError
from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonCog, DigimonLogic
from dg01.games.digimon import DigimonLogic
from dg01.manager import GameManager
from dg01.session import GameSession
from discord.ext import commands
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict
from typing import Dict, List
from typing import Optional
import asyncio
import discord
import json
import logging
import sys
import traceback

# Generated on 2024-11-19 23:22:39

# ===== merged_output.py =====
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from dg01.const import GameType
from dg01.const import GameType, GameState
from dg01.errors import GameError
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError
from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonCog, DigimonLogic
from dg01.games.digimon import DigimonLogic
from dg01.manager import GameManager
from dg01.session import GameSession
from discord.ext import commands
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict
from typing import Dict, List
from typing import Optional
import asyncio
import discord
import json
import logging
import sys
import traceback

# Generated on 2024-11-19 23:17:22

# ===== merged_output.py =====
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from dg01.const import GameType
from dg01.const import GameType, GameState
from dg01.errors import GameError
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonCog, DigimonLogic
from dg01.games.digimon import DigimonLogic
from dg01.manager import GameManager
from dg01.session import GameSession
from discord.ext import commands
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict
from typing import Dict, List
from typing import Optional
import asyncio
import discord
import json
import logging
import sys
import traceback

# Generated on 2024-11-19 23:13:15

# ===== merged_output.py =====
# Generated on 2024-11-19 23:13:05

# ===== const.py =====
import asyncio
from enum import Enum
from dataclasses import dataclass


@dataclass
class GameEvent:
    type: str
    data: dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = asyncio.get_event_loop().time()


class GameType(Enum):
    DIGIMON = "디지몬"
    # POKEMON = "포켓몬"
    # YUGIOH = "유희왕"
    # 필요한 게임 타입 추가 가능


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


# ===== __init__.py =====
import sys
import logging
import traceback
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone

import discord


def setup_logger(name: str) -> logging.Logger:
    """
    모든 모듈에서 공유하는 단일 로거를 설정합니다.
    
    Args:
        name (str): 로거의 이름 (모듈별 구분용)
    
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    
    # 로거 생성
    logger = logging.getLogger(name)
    
    # 로거가 이미 핸들러를 가지고 있다면 추가 설정하지 않음
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 로그 디렉토리 생성
    log_dir = Path('__logs')
    log_dir.mkdir(exist_ok=True)
    
    # 포맷터 생성 - 모듈 이름을 포함하도록 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 공용 파일 핸들러 설정
    file_handler = RotatingFileHandler(
        f'{log_dir}/game_errors.log',
        maxBytes=1024 * 1024 * 5,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class GameError(Exception):
    """
    게임 관련 에러를 처리하는 기본 예외 클래스
    """
    def __init__(self, message: str, error_code: str = None, should_notify: bool = True):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'GAME_ERROR'
        self.should_notify = should_notify
        self.timestamp = datetime.now(timezone.utc) + timedelta(hours=9)
        
        # 서버 로깅
        self.log_error()
    
    def log_error(self):
        """에러를 서버 콘솔과 로그 파일에 기록"""
        error_msg = self.format_error()
        
        # 콘솔 출력
        print(error_msg)
        
        # 로그 파일에 기록
        logger.error(error_msg, exc_info=True)
    
    def format_error(self) -> str:
        """에러 메시지 포맷팅"""
        return (
            f"\n{'='*50}\n"
            f"Error Code: {self.error_code}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Message: {self.message}\n"
            f"Stack Trace:\n{traceback.format_exc()}\n"
            f"{'='*50}"
        )
    
    async def notify_discord(self, ctx) -> None:
        """디스코드 채널에 에러 메시지 전송"""
        if not self.should_notify or not ctx:
            return
            
        try:
            embed = discord.Embed(
                title="Game Error",
                description=self.message,
                color=discord.Color.red(),
                timestamp=self.timestamp
            )
            
            embed.add_field(
                name="Error Code",
                value=self.error_code,
                inline=True
            )
            
            embed.set_footer(text="Please try again or contact a moderator if the issue persists.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to send error message to Discord: {str(e)}")


class GameCriticalError(GameError):
    """
    게임의 진행이 불가능한 심각한 오류를 나타내는 예외 클래스
    예: 데이터 손상, 필수 리소스 접근 불가 등
    """
    pass

class InvalidActionError(GameError):
    """
    잘못된 게임 액션을 나타내는 예외 클래스
    예: 잘못된 위치에 말을 놓으려고 할 때
    """
    pass

class GameSessionError(GameError):
    """
    게임 세션 관련 오류를 나타내는 예외 클래스
    예: 이미 존재하는 세션, 찾을 수 없는 세션 등
    """
    pass


logger = setup_logger('game_error')

# ===== events.py =====
from typing import Dict, List


class EventBus:
    def __init__(self):
        # 이벤트 타입별 구독자(콜백 함수) 목록을 저장하는 딕셔너리
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: str, callback: callable):
        """
        특정 이벤트 타입에 대한 구독자(콜백 함수) 등록
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 발생 시 호출될 콜백 함수
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event_type: str, data: dict):
        """
        이벤트 발행 및 구독자들에게 통지
        
        Args:
            event_type: 발행할 이벤트 타입
            data: 이벤트와 함께 전달할 데이터
        """
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                await callback(data)
# ===== __init__.py =====

# ===== base.py =====

class GameLogic:
    def __init__(self):
        pass
# ===== digimon.py =====
from discord.ext import commands

from dg01.games.base import GameLogic
from dg01.errors import GameError


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    @commands.command()
    async def create(self, ctx):
        try:
            await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, "digimon")
        except GameError as e:
            await ctx.send(str(e))   
    """

    @commands.command(name="쓰담쓰담")
    async def start(self, ctx):
        try:
            await self.bot.game_manager.handle_command(ctx, "start")
            await ctx.send('쓰담쓰담 쓰담쓰담')
        except GameError as e:
            await ctx.send(str(e))   

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')


class DigimonLogic(GameLogic):
    def __init__(self):
        pass

    def update(self, delta_time):
        events = []
        print(f"DigimonLogic update called - {delta_time=}")
        return events

# ===== main.py =====
import json
from pathlib import Path

import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.manager import GameManager
from dg01.const import GameType


logger = setup_logger(__name__)


class GameCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='시작')
    async def start_game(self, ctx: commands.Context, game_type_str: str):
        """게임 시작 명령어"""
        try:
            game_type = GameType(game_type_str.lower())
            success = await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, game_type)
            if success:
                await ctx.send(f"{game_type} 게임이 시작되었습니다!")
            else:
                await ctx.send("이미 게임이 실행 중입니다.")
        except ValueError:
            await ctx.send(f"지원하지 않는 게임 타입입니다. 지원 게임: {', '.join(type.value for type in GameType)}")

    @commands.command(name='종료')
    async def end_game(self, ctx: commands.Context):
        """게임 종료 명령어"""
        success = await self.bot.game_manager.end_game(ctx.channel.id)
        if success:
            await ctx.send("게임이 종료되었습니다.")
        else:
            await ctx.send("실행 중인 게임이 없습니다.")


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.game_manager = GameManager(self)
    
    async def setup_hook(self):
        print("GameBot.setup_hook called")
        await self.add_cog(GameCommandsCog(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')
            

if __name__ == "__main__":
    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()
    bot.run(token)

# ===== manager.py =====
from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.session import GameSession
from dg01.events import EventBus
from dg01.errors import GameError
from dg01.const import GameType
from dg01.games.digimon import DigimonCog, DigimonLogic


class GameManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: Dict[int, GameSession] = {}

        self.event_bus = EventBus()
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        self.event_bus.subscribe("game_started", self.handle_game_started)
        self.event_bus.subscribe("game_error", self.handle_game_error)
    
    async def create_game(self, user_id: int, channel_id: int, game_type: GameType) -> GameSession:
        if user_id in self.sessions:
            return GameError("You already have an active game")
        else:
            session = GameSession(user_id=user_id, event_bus=self.event_bus, game_type=game_type)
            session.channel_id = channel_id
            self.sessions[user_id] = session

            message = await self.send_game_message(channel_id)
            session.message_id = message.id
            
            if game_type == GameType.DIGIMON:
                await self.bot.add_cog(DigimonCog(self.bot))
            else:
                raise GameError(f"Unknown game type for cog: {game_type}")
            
            return session
        
    async def end_game(self, channel_id: int) -> bool:
        """
        try:
            if channel_id not in self.active_games:
                return False

            game_type = self.active_games[channel_id]
            del self.active_games[channel_id]

            # 해당 게임 타입이 다른 채널에서 사용되고 있는지 확인
            if game_type not in [game for game in self.active_games.values()]:
                # 아무 채널에서도 사용되지 않는다면 Cog 제거
                if game_type in self.game_cogs:
                    await self.bot.remove_cog(self.game_cogs[game_type].qualified_name)
                    del self.game_cogs[game_type]

            return True

        except Exception as e:
            print(f"Error ending game: {e}")
            return False
        """
        pass
    
    async def handle_game_started(self, data: dict):
        """게임 시작 이벤트 처리"""
        channel = self.bot.get_channel(data.get("channel_id"))
        if channel:
            await channel.send(f"Game started by user {data['user_id']}")
        else:
            raise GameError("Failed to get channel.")
        
    async def handle_game_error(self, data: dict):
        """게임 에러 이벤트 처리"""
        channel = self.bot.get_channel(data.get("channel_id"))
        if channel:
            await channel.send(f"Error {data['error_message']}")
        else:
            raise GameError("Failed to get channel.")

    async def handle_command(self, ctx: commands.Context, command: str, *args):
        session = self.sessions.get(ctx.author.id)  # Changed from channel_id to author.id
        if not session:
            raise GameError("You don't have an active game")

        if command == "start":
            await session.start_game()
        else:
            pass        

    async def send_game_message(self, channel_id: int) -> discord.Message:
        """
        게임 상태를 보여주는 메시지를 전송합니다.
        
        Args:
            channel_id (int): 메시지를 전송할 채널 ID
            
        Returns:
            discord.Message: 전송된 디스코드 메시지 객체
        """
        channel = self.bot.get_channel(channel_id)
        if not channel:
            raise GameError(f"Cannot find channel with ID {channel_id}")

        # 기본 게임 임베드 생성
        embed = discord.Embed(
            title="New Game",
            description="Game is being initialized...",
            color=discord.Color.blue()
        )
        
        # 컨트롤 설명 추가
        embed.add_field(
            name="Controls",
            value="Use the following commands:\n"
                  "• `!move <x> <y>` - Make a move\n"
                  "• `!endgame` - End the current game",
            inline=False
        )
        
        # 게임 상태 필드 추가
        embed.add_field(
            name="Status",
            value="Waiting for players...",
            inline=True
        )
        
        # 현재 시간 추가
        embed.timestamp = datetime.now(timezone.utc) + timedelta(hours=9)
        
        # 게임 보드나 추가 정보를 위한 자리 표시자
        embed.add_field(
            name="Game Board",
            value="Loading...",
            inline=False
        )
        
        # 메시지 전송
        try:
            message = await channel.send(embed=embed)
            
            # 필요한 경우 반응 이모지 추가
            # await message.add_reaction("▶️")  # 시작
            # await message.add_reaction("⏹️")  # 종료
            
            return message
            
        except discord.Forbidden:
            raise GameError("Bot doesn't have permission to send messages in this channel")
        except discord.HTTPException as e:
            raise GameError(f"Failed to send game message: {str(e)}")
# ===== session.py =====
import asyncio
from typing import Optional

from discord.ext import commands

from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.const import GameType, GameState
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonLogic


logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, event_bus: EventBus, game_type: GameType):
        self.user_id = user_id
        self.event_bus = event_bus
        self.game_type = game_type
        self.game_logic = self.create_game_logic(game_type)
        self.state = GameState.WAITING
        self.channel_id: Optional[int] = None
        self.tick_rate = 1.0   

    def create_game_logic(self, game_type: GameType) -> GameLogic:
        if game_type == GameType.DIGIMON:
            return DigimonLogic()
        else:
            raise GameError(f"Unknown game type for create_game_logic: {game_type}")
    
    async def start_game(self):
        if self.state != GameState.WAITING:
            raise GameError("Game already started")
        
        self.state = GameState.PLAYING
        self.last_update = asyncio.get_event_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

    async def update_loop(self):  # not used yet
        try:
            while self.state == GameState.PLAYING:
                current_time = asyncio.get_event_loop().time()
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
                sleep_time = max(0, next_update - asyncio.get_event_loop().time())
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            await self.cleanup()
        except Exception as e:
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
            await self.event_bus.publish("game_cleanup", {
                "user_id": self.user_id,
                "channel_id": self.channel_id,
                "game_type": self.game_type
            })

            # 게임 상태를 FINISHED로 변경
            self.state = GameState.FINISHED

            logger.info(f"Cleaned up game session for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error during cleanup for user {self.user_id}: {str(e)}")

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
                "session_id": str(self.user_id),
                "game_type": self.game_type,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }

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
            await self.event_bus.publish("game_error", {
                "user_id": self.user_id,
                "error_info": error_info,
                "channel_id": self.channel_id,
                "severity": severity
            })
        except Exception as e:
            logger.critical(f"Error in error handler: {str(e)}")
            if ctx:
                try:
                    await ctx.send("An unexpected error occurred in the error handler.")
                except:
                    pass
# ===== const.py =====
import asyncio
from enum import Enum
from dataclasses import dataclass


@dataclass
class GameEvent:
    type: str
    data: dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = asyncio.get_event_loop().time()


class GameType(Enum):
    DIGIMON = "디지몬"
    # POKEMON = "포켓몬"
    # YUGIOH = "유희왕"
    # 필요한 게임 타입 추가 가능


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


# ===== __init__.py =====
import sys
import logging
import traceback
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone

import discord


def setup_logger(name: str) -> logging.Logger:
    """
    모든 모듈에서 공유하는 단일 로거를 설정합니다.
    
    Args:
        name (str): 로거의 이름 (모듈별 구분용)
    
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    
    # 로거 생성
    logger = logging.getLogger(name)
    
    # 로거가 이미 핸들러를 가지고 있다면 추가 설정하지 않음
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 로그 디렉토리 생성
    log_dir = Path('__logs')
    log_dir.mkdir(exist_ok=True)
    
    # 포맷터 생성 - 모듈 이름을 포함하도록 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 공용 파일 핸들러 설정
    file_handler = RotatingFileHandler(
        f'{log_dir}/game_errors.log',
        maxBytes=1024 * 1024 * 5,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class GameError(Exception):
    """
    게임 관련 에러를 처리하는 기본 예외 클래스
    """
    def __init__(self, message: str, error_code: str = None, should_notify: bool = True):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'GAME_ERROR'
        self.should_notify = should_notify
        self.timestamp = datetime.now(timezone.utc) + timedelta(hours=9)
        
        # 서버 로깅
        self.log_error()
    
    def log_error(self):
        """에러를 서버 콘솔과 로그 파일에 기록"""
        error_msg = self.format_error()
        
        # 콘솔 출력
        print(error_msg)
        
        # 로그 파일에 기록
        logger.error(error_msg, exc_info=True)
    
    def format_error(self) -> str:
        """에러 메시지 포맷팅"""
        return (
            f"\n{'='*50}\n"
            f"Error Code: {self.error_code}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Message: {self.message}\n"
            f"Stack Trace:\n{traceback.format_exc()}\n"
            f"{'='*50}"
        )
    
    async def notify_discord(self, ctx) -> None:
        """디스코드 채널에 에러 메시지 전송"""
        if not self.should_notify or not ctx:
            return
            
        try:
            embed = discord.Embed(
                title="Game Error",
                description=self.message,
                color=discord.Color.red(),
                timestamp=self.timestamp
            )
            
            embed.add_field(
                name="Error Code",
                value=self.error_code,
                inline=True
            )
            
            embed.set_footer(text="Please try again or contact a moderator if the issue persists.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to send error message to Discord: {str(e)}")


class GameCriticalError(GameError):
    """
    게임의 진행이 불가능한 심각한 오류를 나타내는 예외 클래스
    예: 데이터 손상, 필수 리소스 접근 불가 등
    """
    pass

class InvalidActionError(GameError):
    """
    잘못된 게임 액션을 나타내는 예외 클래스
    예: 잘못된 위치에 말을 놓으려고 할 때
    """
    pass

class GameSessionError(GameError):
    """
    게임 세션 관련 오류를 나타내는 예외 클래스
    예: 이미 존재하는 세션, 찾을 수 없는 세션 등
    """
    pass


logger = setup_logger('game_error')

# ===== events.py =====
from typing import Dict, List


class EventBus:
    def __init__(self):
        # 이벤트 타입별 구독자(콜백 함수) 목록을 저장하는 딕셔너리
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: str, callback: callable):
        """
        특정 이벤트 타입에 대한 구독자(콜백 함수) 등록
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 발생 시 호출될 콜백 함수
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event_type: str, data: dict):
        """
        이벤트 발행 및 구독자들에게 통지
        
        Args:
            event_type: 발행할 이벤트 타입
            data: 이벤트와 함께 전달할 데이터
        """
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                await callback(data)
# ===== __init__.py =====

# ===== base.py =====

class GameLogic:
    def __init__(self):
        pass
# ===== digimon.py =====
from discord.ext import commands

from dg01.games.base import GameLogic
from dg01.errors import GameError


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    @commands.command()
    async def create(self, ctx):
        try:
            await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, "digimon")
        except GameError as e:
            await ctx.send(str(e))   
    """

    @commands.command(name="쓰담쓰담")
    async def start(self, ctx):
        try:
            await self.bot.game_manager.handle_command(ctx, "start")
            await ctx.send('쓰담쓰담 쓰담쓰담')
        except GameError as e:
            await ctx.send(str(e))   

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')


class DigimonLogic(GameLogic):
    def __init__(self):
        pass

    def update(self, delta_time):
        events = []
        print(f"DigimonLogic update called - {delta_time=}")
        return events

# ===== main.py =====
import json
from pathlib import Path

import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.manager import GameManager
from dg01.const import GameType


logger = setup_logger(__name__)


class GameCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='시작')
    async def start_game(self, ctx: commands.Context, game_type_str: str):
        """게임 시작 명령어"""
        try:
            game_type = GameType(game_type_str.lower())
            success = await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, game_type)
            if success:
                await ctx.send(f"{game_type} 게임이 시작되었습니다!")
            else:
                await ctx.send("이미 게임이 실행 중입니다.")
        except ValueError:
            await ctx.send(f"지원하지 않는 게임 타입입니다. 지원 게임: {', '.join(type.value for type in GameType)}")

    @commands.command(name='종료')
    async def end_game(self, ctx: commands.Context):
        """게임 종료 명령어"""
        success = await self.bot.game_manager.end_game(ctx.channel.id)
        if success:
            await ctx.send("게임이 종료되었습니다.")
        else:
            await ctx.send("실행 중인 게임이 없습니다.")


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.game_manager = GameManager(self)
    
    async def setup_hook(self):
        print("GameBot.setup_hook called")
        await self.add_cog(GameCommandsCog(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')
            

if __name__ == "__main__":
    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()
    bot.run(token)

# ===== manager.py =====
from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.session import GameSession
from dg01.events import EventBus
from dg01.errors import setup_logger, GameError
from dg01.const import GameType
from dg01.games.digimon import DigimonCog, DigimonLogic


logger = setup_logger(__name__)


class GameManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: Dict[int, GameSession] = {}

        self.event_bus = EventBus()
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        self.event_bus.subscribe("game_started", self.handle_game_started)
        self.event_bus.subscribe("game_error", self.handle_game_error)
    
    async def create_game(self, user_id: int, channel_id: int, game_type: GameType) -> GameSession:
        if user_id in self.sessions:
            return GameError("You already have an active game")
        else:
            session = GameSession(user_id=user_id, event_bus=self.event_bus, game_type=game_type)
            session.channel_id = channel_id
            self.sessions[user_id] = session

            message = await self.send_game_message(channel_id)
            session.message_id = message.id
            
            if game_type == GameType.DIGIMON:
                await self.bot.add_cog(DigimonCog(self.bot))
            else:
                raise GameError(f"Unknown game type for cog: {game_type}")
            
            return session
        
    async def end_game(self, channel_id: int) -> bool:
        """
        게임 세션을 종료하고 관련 리소스를 정리합니다.
        
        Args:
            channel_id (int): 게임이 실행 중인 디스코드 채널 ID
            
        Returns:
            bool: 게임이 성공적으로 종료되면 True, 실행 중인 게임이 없으면 False
        """
        try:
            # 채널 ID로 세션 찾기
            session = next((s for s in self.sessions.values() if s.channel_id == channel_id), None)
            if not session:
                return False

            # 세션 정리 
            await session.cleanup()
            
            # 게임 타입에 따른 Cog 제거
            if session.game_type == GameType.DIGIMON:
                await self.bot.remove_cog(DigimonCog(self.bot).qualified_name)
                
            # 활성 세션에서 제거
            del self.sessions[session.user_id]
            
            return True
            
        except Exception as e:
            logger.error(f"게임 종료 중 오류 발생: {str(e)}")
            return False
        
    async def handle_game_started(self, data: dict):
        """게임 시작 이벤트 처리"""
        channel = self.bot.get_channel(data.get("channel_id"))
        if channel:
            await channel.send(f"Game started by user {data['user_id']}")
        else:
            raise GameError("Failed to get channel.")
        
    async def handle_game_error(self, data: dict):
        """게임 에러 이벤트 처리"""
        channel = self.bot.get_channel(data.get("channel_id"))
        if channel:
            await channel.send(f"Error {data['error_message']}")
        else:
            raise GameError("Failed to get channel.")

    async def handle_command(self, ctx: commands.Context, command: str, *args):
        session = self.sessions.get(ctx.author.id)  # Changed from channel_id to author.id
        if not session:
            raise GameError("You don't have an active game")

        if command == "start":
            await session.start_game()
        else:
            pass        

    async def send_game_message(self, channel_id: int) -> discord.Message:
        """
        게임 상태를 보여주는 메시지를 전송합니다.
        
        Args:
            channel_id (int): 메시지를 전송할 채널 ID
            
        Returns:
            discord.Message: 전송된 디스코드 메시지 객체
        """
        channel = self.bot.get_channel(channel_id)
        if not channel:
            raise GameError(f"Cannot find channel with ID {channel_id}")

        # 기본 게임 임베드 생성
        embed = discord.Embed(
            title="New Game",
            description="Game is being initialized...",
            color=discord.Color.blue()
        )
        
        # 컨트롤 설명 추가
        embed.add_field(
            name="Controls",
            value="Use the following commands:\n"
                  "• `!move <x> <y>` - Make a move\n"
                  "• `!endgame` - End the current game",
            inline=False
        )
        
        # 게임 상태 필드 추가
        embed.add_field(
            name="Status",
            value="Waiting for players...",
            inline=True
        )
        
        # 현재 시간 추가
        embed.timestamp = datetime.now(timezone.utc) + timedelta(hours=9)
        
        # 게임 보드나 추가 정보를 위한 자리 표시자
        embed.add_field(
            name="Game Board",
            value="Loading...",
            inline=False
        )
        
        # 메시지 전송
        try:
            message = await channel.send(embed=embed)
            
            # 필요한 경우 반응 이모지 추가
            # await message.add_reaction("▶️")  # 시작
            # await message.add_reaction("⏹️")  # 종료
            
            return message
            
        except discord.Forbidden:
            raise GameError("Bot doesn't have permission to send messages in this channel")
        except discord.HTTPException as e:
            raise GameError(f"Failed to send game message: {str(e)}")
# ===== session.py =====
import asyncio
from typing import Optional

from discord.ext import commands

from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.const import GameType, GameState
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonLogic


logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, event_bus: EventBus, game_type: GameType):
        self.user_id = user_id
        self.event_bus = event_bus
        self.game_type = game_type
        self.game_logic = self.create_game_logic(game_type)
        self.state = GameState.WAITING
        self.channel_id: Optional[int] = None
        self.tick_rate = 1.0   

    def create_game_logic(self, game_type: GameType) -> GameLogic:
        if game_type == GameType.DIGIMON:
            return DigimonLogic()
        else:
            raise GameError(f"Unknown game type for create_game_logic: {game_type}")
    
    async def start_game(self):
        if self.state != GameState.WAITING:
            raise GameError("Game already started")
        
        self.state = GameState.PLAYING
        self.last_update = asyncio.get_event_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

    async def update_loop(self):  # not used yet
        try:
            while self.state == GameState.PLAYING:
                current_time = asyncio.get_event_loop().time()
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
                sleep_time = max(0, next_update - asyncio.get_event_loop().time())
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            await self.cleanup()
        except Exception as e:
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
            await self.event_bus.publish("game_cleanup", {
                "user_id": self.user_id,
                "channel_id": self.channel_id,
                "game_type": self.game_type
            })

            # 게임 상태를 FINISHED로 변경
            self.state = GameState.FINISHED

            logger.info(f"Cleaned up game session for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error during cleanup for user {self.user_id}: {str(e)}")

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
                "session_id": str(self.user_id),
                "game_type": self.game_type,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }

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
            await self.event_bus.publish("game_error", {
                "user_id": self.user_id,
                "error_info": error_info,
                "channel_id": self.channel_id,
                "severity": severity
            })
        except Exception as e:
            logger.critical(f"Error in error handler: {str(e)}")
            if ctx:
                try:
                    await ctx.send("An unexpected error occurred in the error handler.")
                except:
                    pass
# ===== const.py =====
import asyncio
from enum import Enum
from dataclasses import dataclass


@dataclass
class GameEvent:
    type: str
    data: dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = asyncio.get_event_loop().time()


class GameType(Enum):
    DIGIMON = "디지몬"
    # POKEMON = "포켓몬"
    # YUGIOH = "유희왕"
    # 필요한 게임 타입 추가 가능


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


# ===== __init__.py =====
import sys
import logging
import traceback
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone

import discord


def setup_logger(name: str) -> logging.Logger:
    """
    모든 모듈에서 공유하는 단일 로거를 설정합니다.
    
    Args:
        name (str): 로거의 이름 (모듈별 구분용)
    
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    
    # 로거 생성
    logger = logging.getLogger(name)
    
    # 로거가 이미 핸들러를 가지고 있다면 추가 설정하지 않음
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # 로그 디렉토리 생성
    log_dir = Path('__logs')
    log_dir.mkdir(exist_ok=True)
    
    # 포맷터 생성 - 모듈 이름을 포함하도록 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 공용 파일 핸들러 설정
    file_handler = RotatingFileHandler(
        f'{log_dir}/game_errors.log',
        maxBytes=1024 * 1024 * 5,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class GameError(Exception):
    """
    게임 관련 에러를 처리하는 기본 예외 클래스
    """
    def __init__(self, message: str, error_code: str = None, should_notify: bool = True):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'GAME_ERROR'
        self.should_notify = should_notify
        self.timestamp = datetime.now(timezone.utc) + timedelta(hours=9)
        
        # 서버 로깅
        self.log_error()
    
    def log_error(self):
        """에러를 서버 콘솔과 로그 파일에 기록"""
        error_msg = self.format_error()
        
        # 콘솔 출력
        print(error_msg)
        
        # 로그 파일에 기록
        logger.error(error_msg, exc_info=True)
    
    def format_error(self) -> str:
        """에러 메시지 포맷팅"""
        return (
            f"\n{'='*50}\n"
            f"Error Code: {self.error_code}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Message: {self.message}\n"
            f"Stack Trace:\n{traceback.format_exc()}\n"
            f"{'='*50}"
        )
    
    async def notify_discord(self, ctx) -> None:
        """디스코드 채널에 에러 메시지 전송"""
        if not self.should_notify or not ctx:
            return
            
        try:
            embed = discord.Embed(
                title="Game Error",
                description=self.message,
                color=discord.Color.red(),
                timestamp=self.timestamp
            )
            
            embed.add_field(
                name="Error Code",
                value=self.error_code,
                inline=True
            )
            
            embed.set_footer(text="Please try again or contact a moderator if the issue persists.")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to send error message to Discord: {str(e)}")


class GameCriticalError(GameError):
    """
    게임의 진행이 불가능한 심각한 오류를 나타내는 예외 클래스
    예: 데이터 손상, 필수 리소스 접근 불가 등
    """
    pass

class InvalidActionError(GameError):
    """
    잘못된 게임 액션을 나타내는 예외 클래스
    예: 잘못된 위치에 말을 놓으려고 할 때
    """
    pass

class GameSessionError(GameError):
    """
    게임 세션 관련 오류를 나타내는 예외 클래스
    예: 이미 존재하는 세션, 찾을 수 없는 세션 등
    """
    pass


logger = setup_logger('game_error')

# ===== events.py =====
from typing import Dict, List


class EventBus:
    def __init__(self):
        # 이벤트 타입별 구독자(콜백 함수) 목록을 저장하는 딕셔너리
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: str, callback: callable):
        """
        특정 이벤트 타입에 대한 구독자(콜백 함수) 등록
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 발생 시 호출될 콜백 함수
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event_type: str, data: dict):
        """
        이벤트 발행 및 구독자들에게 통지
        
        Args:
            event_type: 발행할 이벤트 타입
            data: 이벤트와 함께 전달할 데이터
        """
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                await callback(data)
# ===== __init__.py =====

# ===== base.py =====

class GameLogic:
    def __init__(self):
        pass
# ===== digimon.py =====
from discord.ext import commands

from dg01.games.base import GameLogic
from dg01.errors import GameError


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    @commands.command()
    async def create(self, ctx):
        try:
            await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, "digimon")
        except GameError as e:
            await ctx.send(str(e))   
    """

    @commands.command(name="쓰담쓰담")
    async def start(self, ctx):
        try:
            await self.bot.game_manager.handle_command(ctx, "start")
            await ctx.send('쓰담쓰담 쓰담쓰담')
        except GameError as e:
            await ctx.send(str(e))   

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')


class DigimonLogic(GameLogic):
    def __init__(self):
        pass

    def update(self, delta_time):
        events = []
        print(f"DigimonLogic update called - {delta_time=}")
        return events

# ===== main.py =====
import json
from pathlib import Path

import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.manager import GameManager
from dg01.const import GameType


logger = setup_logger(__name__)


class GameCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='시작')
    async def start_game(self, ctx: commands.Context, game_type_str: str):
        """게임 시작 명령어"""
        try:
            game_type = GameType(game_type_str.lower())
            success = await self.bot.game_manager.create_game(ctx.author.id, ctx.channel.id, game_type)
            if success:
                await ctx.send(f"{game_type} 게임이 시작되었습니다!")
            else:
                await ctx.send("이미 게임이 실행 중입니다.")
        except ValueError:
            await ctx.send(f"지원하지 않는 게임 타입입니다. 지원 게임: {', '.join(type.value for type in GameType)}")

    @commands.command(name='종료')
    async def end_game(self, ctx: commands.Context, game_type_str: str):
        """게임 종료 명령어"""
        game_type = GameType(game_type_str.lower())
        success = await self.bot.game_manager.end_game(ctx.author.id, game_type)
        if success:
            await ctx.send(f"{game_type} 게임이 종료되었습니다.")
        else:
            await ctx.send("실행 중인 게임이 없습니다.")


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.game_manager = GameManager(self)
    
    async def setup_hook(self):
        print("GameBot.setup_hook called")
        await self.add_cog(GameCommandsCog(self))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')
            

if __name__ == "__main__":
    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()
    bot.run(token)

# ===== manager.py =====
from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.session import GameSession
from dg01.events import EventBus
from dg01.errors import setup_logger, GameError
from dg01.const import GameType
from dg01.games.digimon import DigimonCog, DigimonLogic


logger = setup_logger(__name__)


class GameManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: Dict[int, GameSession] = {}  # user_id: GameSession

        self.event_bus = EventBus()
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        self.event_bus.subscribe("game_started", self.handle_game_started)
        self.event_bus.subscribe("game_error", self.handle_game_error)
    
    async def create_game(self, user_id: int, channel_id: int, game_type: GameType) -> GameSession:
        if user_id in self.sessions:
            return GameError("You already have an active game")
        else:
            session = GameSession(user_id=user_id, event_bus=self.event_bus, game_type=game_type)
            session.channel_id = channel_id
            self.sessions[user_id] = session

            message = await self.send_game_message(channel_id)
            session.message_id = message.id
            
            if game_type == GameType.DIGIMON:
                await self.bot.add_cog(DigimonCog(self.bot))
            else:
                raise GameError(f"Unknown game type for cog: {game_type}")
            
            return session
        
    async def end_game(self, user_id: int, game_type: GameType) -> bool:
        pass
        
    async def handle_game_started(self, data: dict):
        """게임 시작 이벤트 처리"""
        channel = self.bot.get_channel(data.get("channel_id"))
        if channel:
            await channel.send(f"Game started by user {data['user_id']}")
        else:
            raise GameError("Failed to get channel.")
        
    async def handle_game_error(self, data: dict):
        """게임 에러 이벤트 처리"""
        channel = self.bot.get_channel(data.get("channel_id"))
        if channel:
            await channel.send(f"Error {data['error_message']}")
        else:
            raise GameError("Failed to get channel.")

    async def handle_command(self, ctx: commands.Context, command: str, *args):
        session = self.sessions.get(ctx.author.id)  # Changed from channel_id to author.id
        if not session:
            raise GameError("You don't have an active game")

        if command == "start":
            await session.start_game()
        else:
            pass        

    async def send_game_message(self, channel_id: int) -> discord.Message:
        """
        게임 상태를 보여주는 메시지를 전송합니다.
        
        Args:
            channel_id (int): 메시지를 전송할 채널 ID
            
        Returns:
            discord.Message: 전송된 디스코드 메시지 객체
        """
        channel = self.bot.get_channel(channel_id)
        if not channel:
            raise GameError(f"Cannot find channel with ID {channel_id}")

        # 기본 게임 임베드 생성
        embed = discord.Embed(
            title="New Game",
            description="Game is being initialized...",
            color=discord.Color.blue()
        )
        
        # 컨트롤 설명 추가
        embed.add_field(
            name="Controls",
            value="Use the following commands:\n"
                  "• `!move <x> <y>` - Make a move\n"
                  "• `!endgame` - End the current game",
            inline=False
        )
        
        # 게임 상태 필드 추가
        embed.add_field(
            name="Status",
            value="Waiting for players...",
            inline=True
        )
        
        # 현재 시간 추가
        embed.timestamp = datetime.now(timezone.utc) + timedelta(hours=9)
        
        # 게임 보드나 추가 정보를 위한 자리 표시자
        embed.add_field(
            name="Game Board",
            value="Loading...",
            inline=False
        )
        
        # 메시지 전송
        try:
            message = await channel.send(embed=embed)
            
            # 필요한 경우 반응 이모지 추가
            # await message.add_reaction("▶️")  # 시작
            # await message.add_reaction("⏹️")  # 종료
            
            return message
            
        except discord.Forbidden:
            raise GameError("Bot doesn't have permission to send messages in this channel")
        except discord.HTTPException as e:
            raise GameError(f"Failed to send game message: {str(e)}")
# ===== session.py =====
import asyncio
from typing import Optional

from discord.ext import commands

from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.const import GameType, GameState
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonLogic


logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, event_bus: EventBus, game_type: GameType):
        self.user_id = user_id
        self.event_bus = event_bus
        self.game_type = game_type
        self.game_logic = self.create_game_logic(game_type)
        self.state = GameState.WAITING
        self.channel_id: Optional[int] = None
        self.tick_rate = 1.0   

    def create_game_logic(self, game_type: GameType) -> GameLogic:
        if game_type == GameType.DIGIMON:
            return DigimonLogic()
        else:
            raise GameError(f"Unknown game type for create_game_logic: {game_type}")
    
    async def start_game(self):
        if self.state != GameState.WAITING:
            raise GameError("Game already started")
        
        self.state = GameState.PLAYING
        self.last_update = asyncio.get_event_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

    async def update_loop(self):  # not used yet
        try:
            while self.state == GameState.PLAYING:
                current_time = asyncio.get_event_loop().time()
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
                sleep_time = max(0, next_update - asyncio.get_event_loop().time())
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            await self.cleanup()
        except Exception as e:
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
            await self.event_bus.publish("game_cleanup", {
                "user_id": self.user_id,
                "channel_id": self.channel_id,
                "game_type": self.game_type
            })

            # 게임 상태를 FINISHED로 변경
            self.state = GameState.FINISHED

            logger.info(f"Cleaned up game session for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error during cleanup for user {self.user_id}: {str(e)}")

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
                "session_id": str(self.user_id),
                "game_type": self.game_type,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }

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
            await self.event_bus.publish("game_error", {
                "user_id": self.user_id,
                "error_info": error_info,
                "channel_id": self.channel_id,
                "severity": severity
            })
        except Exception as e:
            logger.critical(f"Error in error handler: {str(e)}")
            if ctx:
                try:
                    await ctx.send("An unexpected error occurred in the error handler.")
                except:
                    pass