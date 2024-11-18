import traceback
import logging
import sys
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

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
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # 포맷터 생성 - 모듈 이름을 포함하도록 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 공용 파일 핸들러 설정
    file_handler = RotatingFileHandler(
        'logs/game_errors.log',
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
