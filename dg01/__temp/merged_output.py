from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from dg01.const import GameType
from dg01.const import GameType, GameState
from dg01.data import GameDataManager
from dg01.errors import GameError
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError
from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonCog, DigimonLogic
from dg01.games.digimon import DigimonLogic
from dg01.games.digimon.cog import DigimonCog
from dg01.games.digimon.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message
from dg01.games.digimon.logic import DigimonLogic
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
import random
import sys
import traceback

# Generated on 2024-11-20 11:29:06

# ===== merged_output.py =====
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from dg01.const import GameType
from dg01.const import GameType, GameState
from dg01.data import GameDataManager
from dg01.errors import GameError
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError
from dg01.errors import setup_logger, GameError, GameCriticalError, InvalidActionError
from dg01.events import EventBus
from dg01.games.base import GameLogic
from dg01.games.digimon import DigimonCog, DigimonLogic
from dg01.games.digimon import DigimonLogic
from dg01.games.digimon.cog import DigimonCog
from dg01.games.digimon.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message
from dg01.games.digimon.logic import DigimonLogic
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
import random
import sys
import traceback

# Generated on 2024-11-20 11:28:52

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
            self.timestamp = asyncio.get_running_loop().time()


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
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

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
            self.timestamp = asyncio.get_running_loop().time()


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
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

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
            self.timestamp = asyncio.get_running_loop().time()


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
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

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
            self.timestamp = asyncio.get_running_loop().time()


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


# ===== data.py =====
from pathlib import Path
from datetime import datetime, timezone
import json

from dg01.errors import setup_logger


logger = setup_logger(__name__)


class GameDataManager:
    def __init__(self, data_dir: str = '__game_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def get_user_data(self, user_id: int, channel_id: int) -> dict:
        """사용자의 게임 데이터를 불러옵니다."""
        default_data = {
            "stage": "디지타마",
            "count": 1,
            "data_absorbed": 0,
            "battles_won": 0,
            "battles_lost": 0,
            "last_cheer": None,
            "is_copying": True,
            "evolution_started": None,
            "channel_id": channel_id,
            "last_played": None
        }
        
        try:
            user_data_file = self.data_dir / f'user_{user_id}.json'
            if user_data_file.exists():
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_data
        except Exception as e:
            logger.error(f"데이터 로드 실패: {str(e)}")
            return default_data
            
    def save_user_data(self, user_id: int, data: dict) -> bool:
        """사용자의 게임 데이터를 저장합니다."""
        try:
            user_data_file = self.data_dir / f'user_{user_id}.json'
            with open(user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"데이터 저장 실패: {str(e)}")
            return False
            
    def update_last_played(self, user_id: int) -> None:
        """사용자의 마지막 플레이 시간을 업데이트합니다."""
        data = self.get_user_data(user_id)
        data["last_played"] = datetime.now(timezone.utc).isoformat()
        self.save_user_data(user_id, data)
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
# ===== __init__.py =====

# ===== cog.py =====
from discord.ext import commands

from dg01.errors import setup_logger


logger = setup_logger(__name__)


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ"])
    async def start(self, ctx: commands.Context):
         await ctx.send('쓰담쓰담 쓰담쓰담')

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')

# ===== config.py =====
GAME_CONFIG = {
    "stages": {
        "디지타마": {
            "evolution_time": 0,
            "evolution_count": 1,
            "copy_rate": 0,
            "data_rate": 0,
            "description": "부화를 기다리는 디지타마입니다. !쓰담쓰담으로 부화시켜주세요.",
            "image_path": "assets/digitama.webp"
        },
        "쿠라몬": {
            "evolution_time": 30,
            "evolution_count": 1010101010,
            "copy_rate": 1.0,  # 1초당 2배로 복제
            "data_rate": 1,    # 1초당 1MB 흡수
            "description": "컴퓨터 네트워크상에 갑자기 출연한 정체불명의 디지몬. 네트워크에서 병원균처럼 번식해 가벼운 네트워크 장애를 일으킵니다.",
            "special_move": "글레어 아이",
            "image_path": "assets/kuramon.webp"
        },
        "츠메몬": {
            "evolution_time": 600,
            "evolution_count": 2000000000,
            "copy_rate": 1.5,  # 1초당 2.5배로 복제
            "data_rate": 10,   # 1초당 10MB 흡수
            "description": "쿠라몬이 더 진화한 유년기 디지몬. 촉수 끝이 갈고리발톱처럼 돼서 더 포악해졌습니다.",
            "special_move": "네일 스크래치",
            "image_path": "assets/tsumemon.webp"
        },
        "케라몬": {
            "evolution_time": 6060,
            "evolution_count": 4000000000,
            "copy_rate": 2.0,  # 1초당 3배로 복제
            "data_rate": 100,  # 1초당 100MB 흡수
            "description": "츠메몬이 진화한 성장기 디지몬. 매우 활기찬 성격으로 파괴 행위는 놀이의 일환이라고 생각합니다.",
            "special_move": "찰싹 때리기",
            "image_path": "assets/kuramon.webp"
        },
        "크리사리몬": {
            "evolution_time": 121000,
            "evolution_count": 8000000000,
            "copy_rate": 2.5,  # 1초당 3.5배로 복제
            "data_rate": 1000, # 1초당 1GB 흡수
            "description": "번데기의 모습을 한 성숙기 디지몬. 이동은 전혀 할 수 없지만 단단한 외피로 보호됩니다.",
            "special_move": "데이터 파괴",
            "image_path": "assets/chrysalimon.webp"
        },
        "인펠몬": {
            "evolution_time": 266400,
            "evolution_count": 16000000000,
            "copy_rate": 3.0,  # 1초당 4배로 복제
            "data_rate": 10000, # 1초당 10GB 흡수
            "description": "손발이 긴 거미의 모습을 한 완전체 디지몬. 강력한 보안과 상관없이 모든 네트워크에 침입할 수 있습니다.",
            "special_move": "네트워크수류탄",
            "image_path": "assets/infermon.webp"
        },
        "디아블로몬": {
            "evolution_time": 600,
            "evolution_count": 0,
            "copy_rate": 0,
            "data_rate": 0,
            "description": "최종 진화 형태. 전지전능한 존재가 되어 핵 미사일 발사 시스템을 해킹했습니다!",
            "special_move": "캐논발사",
            "image_path": "assets/diablomon.webp"
        }
    },
    "battle_chances": {
        "쿠라몬": 1.0,    # 튜토리얼이므로 100% 승리
        "츠메몬": 0.8,    # 80% 승률
        "케라몬": 0.6,    # 60% 승률
        "크리사리몬": 0.5, # 50% 승률
        "인펠몬": 0.4,    # 40% 승률
        "디아블로몬": 0.0  # 전투 없음
    },
    "battle_settings": {
        "battle_chance": 0.1,      # 10% 확률로 전투 발생
        "win_bonus": 1.2,          # 승리시 20% 보너스
        "lose_penalty": 0.8,       # 패배시 20% 감소
        "cheer_bonus": 1.2         # 응원시 승률 20% 증가
    },
    "events": {
        "news": [
            {
                "data_threshold": 1024,  # 1GB
                "message": "전세계 곳곳에서 네트워크 장애 발생! 원인은 알 수 없는 바이러스?"
            },
            {
                "data_threshold": 102400,  # 100GB
                "message": "군사 시설의 네트워크가 뚫렸다! 정체불명의 디지털 생명체 발견!"
            },
            {
                "data_threshold": 1048576,  # 1TB
                "message": "전세계 핵미사일 발사 시스템 해킹 위험! 디아블로몬의 존재 확인!"
            }
        ],
        "random_messages": {
            "쿠라몬": [
                "데이터 맛있어요~",
                "더 많이 복제되고 싶어!"
            ],
            "츠메몬": [
                "네트워크가 약해빠졌네?",
                "더 강한 시스템을 찾아보자!"
            ],
            "케라몬": [
                "파괴는 정말 재미있어!",
                "이 정도 보안은 찰싹이야!"
            ],
            "크리사리몬": [
                "더 강한 힘을 원해...",
                "아무도 날 막을 수 없어"
            ],
            "인펠몬": [
                "이제 곧 최종 진화야!",
                "인류의 모든 데이터를 흡수하겠어!"
            ],
            "디아블로몬": [
                "나는 신이다!",
                "이제 세상은 끝이야!"
            ]
        }
    },
    "evolution_quiz": {
        "쿠라몬": {
            "question": "처음으로 등장한 컴퓨터 바이러스의 이름은?",
            "answer": "크리퍼",
            "hint": "1971년에 만들어진 이 바이러스는 'Creeper'라는 메시지를 출력했습니다."
        },
        "츠메몬": {
            "question": "최초의 웜 바이러스의 이름은?",
            "answer": "모리스 웜",
            "hint": "1988년 로버트 모리스가 만든 이 악성코드는 인터넷 역사상 최초의 웜입니다."
        },
        "케라몬": {
            "question": "램섬웨어의 대표적인 공격 방식은?",
            "answer": "암호화",
            "hint": "피해자의 파일을 이것을 통해 접근할 수 없게 만듭니다."
        },
        "크리사리몬": {
            "question": "DDoS 공격의 풀네임은?",
            "answer": "분산 서비스 거부 공격",
            "hint": "여러 곳에서 동시에 서버를 공격하는 방식입니다."
        },
        "인펠몬": {
            "question": "악성코드를 탐지하는 방법 중 시그니처 기반이 아닌 것은?",
            "answer": "행위기반",
            "hint": "프로그램의 패턴이 아닌 동작을 분석하는 방식입니다."
        }
    }
}

# 스테이지 순서를 리스트로 관리 (진화 순서 체크용)
EVOLUTION_ORDER = [
    "디지타마",
    "쿠라몬",
    "츠메몬",
    "케라몬",
    "크리사리몬", 
    "인펠몬",
    "디아블로몬"
]

# 편의 함수들
def get_next_stage(current_stage: str) -> str:
    """현재 스테이지의 다음 진화 단계를 반환"""
    if current_stage == "디아블로몬":
        return None
    current_index = EVOLUTION_ORDER.index(current_stage)
    return EVOLUTION_ORDER[current_index + 1]

def get_stage_config(stage: str) -> dict:
    """특정 스테이지의 설정을 반환"""
    return GAME_CONFIG["stages"][stage]

def get_battle_chance(stage: str) -> float:
    """특정 스테이지의 기본 전투 승률을 반환"""
    return GAME_CONFIG["battle_chances"].get(stage, 0.0)

def get_random_message(stage: str) -> str:
    """특정 스테이지의 랜덤 대사 중 하나를 반환"""
    import random
    messages = GAME_CONFIG["events"]["random_messages"].get(stage, [])
    return random.choice(messages) if messages else None

def get_evolution_quiz(stage: str) -> dict:
    """특정 스테이지의 진화 퀴즈를 반환"""
    return GAME_CONFIG["evolution_quiz"].get(stage)
# ===== logic.py =====
from dg01.games.base import GameLogic
from dg01.errors import setup_logger, GameError
from dg01.games.digimon.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message


logger = setup_logger(__name__)


class DigimonLogic(GameLogic):
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass

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
from dg01.games.digimon.cog import DigimonCog


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
            session = GameSession(
                user_id=user_id, 
                channel_id=channel_id, 
                event_bus=self.event_bus, 
                game_type=game_type
            )
            self.sessions[user_id] = session

            message = await self.send_game_message(channel_id)
            session.message_id = message.id
            
            if game_type == GameType.DIGIMON:
                await self.bot.add_cog(DigimonCog(self.bot))
            else:
                raise GameError(f"Unknown game type for cog: {game_type}")
            
            return session
            
    async def end_game(self, user_id: int, game_type: GameType) -> bool:
        """
        특정 사용자의 게임 세션을 종료합니다.
        
        Args:
            user_id (int): 게임을 종료할 사용자의 ID
            game_type (GameType): 종료할 게임의 타입
            
        Returns:
            bool: 게임이 정상적으로 종료되면 True, 실행 중인 게임을 찾지 못하면 False
        """
        try:
            # 사용자의 세션 찾기
            session = self.sessions.get(user_id)
            if not session or session.game_type != game_type:
                return False

            # 세션 정리
            await session.cleanup()
            
            # 게임 Cog 제거
            if game_type == GameType.DIGIMON:
                await self.bot.remove_cog(DigimonCog(self.bot).qualified_name)
                
            # 활성 세션 목록에서 제거
            del self.sessions[user_id]
            
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
from dg01.games.digimon.logic import DigimonLogic
from dg01.games.digimon.cog import DigimonCog
from dg01.data import GameDataManager


logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, channel_id: int, event_bus: EventBus, game_type: GameType):
        self.user_id = user_id
        self.channel_id = channel_id
        self.event_bus = event_bus
        self.game_type = game_type
        self.game_logic = self.create_game_logic(game_type)
        self.data_manager = GameDataManager()
        self.state = GameState.WAITING
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
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

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
            self.timestamp = asyncio.get_running_loop().time()


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


# ===== data.py =====
from pathlib import Path
from datetime import datetime, timezone
import json

from dg01.errors import setup_logger


logger = setup_logger(__name__)


class GameDataManager:
    def __init__(self, data_dir: str = '__game_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def get_user_data(self, user_id: int, channel_id: int) -> dict:
        """사용자의 게임 데이터를 불러옵니다."""
        default_data = {
            "stage": "디지타마",
            "count": 1,
            "data_absorbed": 0,
            "battles_won": 0,
            "battles_lost": 0,
            "last_cheer": None,
            "is_copying": True,
            "evolution_started": None,
            "channel_id": channel_id,
            "last_played": None
        }
        
        try:
            user_data_file = self.data_dir / f'user_{user_id}.json'
            if user_data_file.exists():
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_data
        except Exception as e:
            logger.error(f"데이터 로드 실패: {str(e)}")
            return default_data
            
    def save_user_data(self, user_id: int, data: dict) -> bool:
        """사용자의 게임 데이터를 저장합니다."""
        try:
            user_data_file = self.data_dir / f'user_{user_id}.json'
            with open(user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"데이터 저장 실패: {str(e)}")
            return False
            
    def update_last_played(self, user_id: int) -> None:
        """사용자의 마지막 플레이 시간을 업데이트합니다."""
        data = self.get_user_data(user_id)
        data["last_played"] = datetime.now(timezone.utc).isoformat()
        self.save_user_data(user_id, data)
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
# ===== __init__.py =====

# ===== cog.py =====
from discord.ext import commands

from dg01.errors import setup_logger


logger = setup_logger(__name__)


class DigimonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ"])
    async def start(self, ctx: commands.Context):
         await ctx.send('쓰담쓰담 쓰담쓰담')

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await ctx.send('치료 치료')

# ===== config.py =====
GAME_CONFIG = {
    "stages": {
        "디지타마": {
            "evolution_time": 0,
            "evolution_count": 1,
            "copy_rate": 0,
            "data_rate": 0,
            "description": "부화를 기다리는 디지타마입니다. !쓰담쓰담으로 부화시켜주세요.",
            "image_path": "assets/digitama.webp"
        },
        "쿠라몬": {
            "evolution_time": 30,
            "evolution_count": 1010101010,
            "copy_rate": 1.0,  # 1초당 2배로 복제
            "data_rate": 1,    # 1초당 1MB 흡수
            "description": "컴퓨터 네트워크상에 갑자기 출연한 정체불명의 디지몬. 네트워크에서 병원균처럼 번식해 가벼운 네트워크 장애를 일으킵니다.",
            "special_move": "글레어 아이",
            "image_path": "assets/kuramon.webp"
        },
        "츠메몬": {
            "evolution_time": 600,
            "evolution_count": 2000000000,
            "copy_rate": 1.5,  # 1초당 2.5배로 복제
            "data_rate": 10,   # 1초당 10MB 흡수
            "description": "쿠라몬이 더 진화한 유년기 디지몬. 촉수 끝이 갈고리발톱처럼 돼서 더 포악해졌습니다.",
            "special_move": "네일 스크래치",
            "image_path": "assets/tsumemon.webp"
        },
        "케라몬": {
            "evolution_time": 6060,
            "evolution_count": 4000000000,
            "copy_rate": 2.0,  # 1초당 3배로 복제
            "data_rate": 100,  # 1초당 100MB 흡수
            "description": "츠메몬이 진화한 성장기 디지몬. 매우 활기찬 성격으로 파괴 행위는 놀이의 일환이라고 생각합니다.",
            "special_move": "찰싹 때리기",
            "image_path": "assets/kuramon.webp"
        },
        "크리사리몬": {
            "evolution_time": 121000,
            "evolution_count": 8000000000,
            "copy_rate": 2.5,  # 1초당 3.5배로 복제
            "data_rate": 1000, # 1초당 1GB 흡수
            "description": "번데기의 모습을 한 성숙기 디지몬. 이동은 전혀 할 수 없지만 단단한 외피로 보호됩니다.",
            "special_move": "데이터 파괴",
            "image_path": "assets/chrysalimon.webp"
        },
        "인펠몬": {
            "evolution_time": 266400,
            "evolution_count": 16000000000,
            "copy_rate": 3.0,  # 1초당 4배로 복제
            "data_rate": 10000, # 1초당 10GB 흡수
            "description": "손발이 긴 거미의 모습을 한 완전체 디지몬. 강력한 보안과 상관없이 모든 네트워크에 침입할 수 있습니다.",
            "special_move": "네트워크수류탄",
            "image_path": "assets/infermon.webp"
        },
        "디아블로몬": {
            "evolution_time": 600,
            "evolution_count": 0,
            "copy_rate": 0,
            "data_rate": 0,
            "description": "최종 진화 형태. 전지전능한 존재가 되어 핵 미사일 발사 시스템을 해킹했습니다!",
            "special_move": "캐논발사",
            "image_path": "assets/diablomon.webp"
        }
    },
    "battle_chances": {
        "쿠라몬": 1.0,    # 튜토리얼이므로 100% 승리
        "츠메몬": 0.8,    # 80% 승률
        "케라몬": 0.6,    # 60% 승률
        "크리사리몬": 0.5, # 50% 승률
        "인펠몬": 0.4,    # 40% 승률
        "디아블로몬": 0.0  # 전투 없음
    },
    "battle_settings": {
        "battle_chance": 0.1,      # 10% 확률로 전투 발생
        "win_bonus": 1.2,          # 승리시 20% 보너스
        "lose_penalty": 0.8,       # 패배시 20% 감소
        "cheer_bonus": 1.2         # 응원시 승률 20% 증가
    },
    "events": {
        "news": [
            {
                "data_threshold": 1024,  # 1GB
                "message": "전세계 곳곳에서 네트워크 장애 발생! 원인은 알 수 없는 바이러스?"
            },
            {
                "data_threshold": 102400,  # 100GB
                "message": "군사 시설의 네트워크가 뚫렸다! 정체불명의 디지털 생명체 발견!"
            },
            {
                "data_threshold": 1048576,  # 1TB
                "message": "전세계 핵미사일 발사 시스템 해킹 위험! 디아블로몬의 존재 확인!"
            }
        ],
        "random_messages": {
            "쿠라몬": [
                "데이터 맛있어요~",
                "더 많이 복제되고 싶어!"
            ],
            "츠메몬": [
                "네트워크가 약해빠졌네?",
                "더 강한 시스템을 찾아보자!"
            ],
            "케라몬": [
                "파괴는 정말 재미있어!",
                "이 정도 보안은 찰싹이야!"
            ],
            "크리사리몬": [
                "더 강한 힘을 원해...",
                "아무도 날 막을 수 없어"
            ],
            "인펠몬": [
                "이제 곧 최종 진화야!",
                "인류의 모든 데이터를 흡수하겠어!"
            ],
            "디아블로몬": [
                "나는 신이다!",
                "이제 세상은 끝이야!"
            ]
        }
    },
    "evolution_quiz": {
        "쿠라몬": {
            "question": "처음으로 등장한 컴퓨터 바이러스의 이름은?",
            "answer": "크리퍼",
            "hint": "1971년에 만들어진 이 바이러스는 'Creeper'라는 메시지를 출력했습니다."
        },
        "츠메몬": {
            "question": "최초의 웜 바이러스의 이름은?",
            "answer": "모리스 웜",
            "hint": "1988년 로버트 모리스가 만든 이 악성코드는 인터넷 역사상 최초의 웜입니다."
        },
        "케라몬": {
            "question": "램섬웨어의 대표적인 공격 방식은?",
            "answer": "암호화",
            "hint": "피해자의 파일을 이것을 통해 접근할 수 없게 만듭니다."
        },
        "크리사리몬": {
            "question": "DDoS 공격의 풀네임은?",
            "answer": "분산 서비스 거부 공격",
            "hint": "여러 곳에서 동시에 서버를 공격하는 방식입니다."
        },
        "인펠몬": {
            "question": "악성코드를 탐지하는 방법 중 시그니처 기반이 아닌 것은?",
            "answer": "행위기반",
            "hint": "프로그램의 패턴이 아닌 동작을 분석하는 방식입니다."
        }
    }
}

# 스테이지 순서를 리스트로 관리 (진화 순서 체크용)
EVOLUTION_ORDER = [
    "디지타마",
    "쿠라몬",
    "츠메몬",
    "케라몬",
    "크리사리몬", 
    "인펠몬",
    "디아블로몬"
]

# 편의 함수들
def get_next_stage(current_stage: str) -> str:
    """현재 스테이지의 다음 진화 단계를 반환"""
    if current_stage == "디아블로몬":
        return None
    current_index = EVOLUTION_ORDER.index(current_stage)
    return EVOLUTION_ORDER[current_index + 1]

def get_stage_config(stage: str) -> dict:
    """특정 스테이지의 설정을 반환"""
    return GAME_CONFIG["stages"][stage]

def get_battle_chance(stage: str) -> float:
    """특정 스테이지의 기본 전투 승률을 반환"""
    return GAME_CONFIG["battle_chances"].get(stage, 0.0)

def get_random_message(stage: str) -> str:
    """특정 스테이지의 랜덤 대사 중 하나를 반환"""
    import random
    messages = GAME_CONFIG["events"]["random_messages"].get(stage, [])
    return random.choice(messages) if messages else None

def get_evolution_quiz(stage: str) -> dict:
    """특정 스테이지의 진화 퀴즈를 반환"""
    return GAME_CONFIG["evolution_quiz"].get(stage)
# ===== logic.py =====
from dg01.games.base import GameLogic
from dg01.errors import setup_logger, GameError
from dg01.games.digimon.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message


logger = setup_logger(__name__)


class DigimonLogic(GameLogic):
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass

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
from dg01.games.digimon.cog import DigimonCog


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
            session = GameSession(
                user_id=user_id, 
                channel_id=channel_id, 
                event_bus=self.event_bus, 
                game_type=game_type
            )
            self.sessions[user_id] = session

            message = await self.send_game_message(channel_id)
            session.message_id = message.id
            
            if game_type == GameType.DIGIMON:
                await self.bot.add_cog(DigimonCog(self.bot))
            else:
                raise GameError(f"Unknown game type for cog: {game_type}")
            
            return session
            
    async def end_game(self, user_id: int, game_type: GameType) -> bool:
        """
        특정 사용자의 게임 세션을 종료합니다.
        
        Args:
            user_id (int): 게임을 종료할 사용자의 ID
            game_type (GameType): 종료할 게임의 타입
            
        Returns:
            bool: 게임이 정상적으로 종료되면 True, 실행 중인 게임을 찾지 못하면 False
        """
        try:
            # 사용자의 세션 찾기
            session = self.sessions.get(user_id)
            if not session or session.game_type != game_type:
                return False

            # 세션 정리
            await session.cleanup()
            
            # 게임 Cog 제거
            if game_type == GameType.DIGIMON:
                await self.bot.remove_cog(DigimonCog(self.bot).qualified_name)
                
            # 활성 세션 목록에서 제거
            del self.sessions[user_id]
            
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
from dg01.games.digimon.logic import DigimonLogic
from dg01.games.digimon.cog import DigimonCog
from dg01.data import GameDataManager


logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, channel_id: int, event_bus: EventBus, game_type: GameType):
        self.user_id = user_id
        self.channel_id = channel_id
        self.event_bus = event_bus
        self.game_type = game_type
        self.game_logic = self.create_game_logic(game_type)
        self.data_manager = GameDataManager()
        self.state = GameState.WAITING
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
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish("game_started", {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "game_type": self.game_type
        })

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