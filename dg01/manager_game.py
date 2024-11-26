from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.games import GameType, MAPPING__GAME_TYPE__COG_CLASS
from dg01.session import GameSession
from dg01.event_bus import EventBus
from dg01.errors import setup_logger, GameError
from dg01.const import GameEventType
from dg01.manager_data import DataManager


logger = setup_logger(__name__)


class GameManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.sessions: Dict[int, GameSession] = {}  # user_id: GameSession
        self.data_managers: Dict[GameType, DataManager] = {}  # GameType: DataManager
        self.event_bus = EventBus()
        self.cogs: Dict[int, commands.Cog] = {}  # channel_id, Cog  @@@

        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        self.event_bus.subscribe(GameEventType.GAME_STARTED, self.handle_game_started)
        self.event_bus.subscribe(GameEventType.GAME_ERROR, self.handle_game_error)

    async def create_game(self, user_id: int, channel_id: int, game_type: GameType) -> GameSession:
        if game_type in self.data_managers:
            pass
        else:
            self.data_managers[game_type] = DataManager(game_type=game_type)

        self.add_cog(game_type=game_type)
        
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

            # message = await self.send_game_message(channel_id)
            # session.message_id = message.id
            
            """
            if game_type == GameType.DIGIMON:
                await self.bot.add_cog(DigimonCog(self.bot))
            else:
                raise GameError(f"Unknown game type for cog: {game_type}")
            """

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
            
            """
            # 게임 Cog 제거
            if game_type == GameType.DIGIMON:
                await self.bot.remove_cog(DigimonCog(self.bot).qualified_name)
            """

            # 활성 세션 목록에서 제거
            del self.sessions[user_id]
            
            return True
            
        except Exception as e:
            logger.error(f"게임 종료 중 오류 발생: {str(e)}")
            return False

    async def add_cog(self, game_type: GameType):
        CogClass = MAPPING__GAME_TYPE__COG_CLASS.get(game_type)

        if CogClass:
            if self.bot.get_cog(CogClass(self.bot).qualified_name):
                print(f"Cog for {game_type} is aready registered.")
            else:
                await self.bot.add_cog(CogClass(self.bot))
                
            return True
        else:
            raise GameError(f"Unknown game type for cog: {game_type}")

    async def remove_cog(self, game_type: GameType):
        CogClass = MAPPING__GAME_TYPE__COG_CLASS.get(game_type)
        if CogClass:
            await self.bot.remove_cog(CogClass(self.bot).qualified_name)
            return True
        else:
            raise GameError(f"Unknown game type for cog: {game_type}")
        
    async def handle_game_started(self, data: dict):
        """게임 시작 이벤트 처리"""
        channel = self.bot.get_channel(data.channel_id)
        if channel:
            await channel.send(f"Game started by user {data.user_id}")
        else:
            raise GameError("Failed to get channel.")
        
    async def handle_game_error(self, data: dict):
        """게임 에러 이벤트 처리"""
        channel = self.bot.get_channel(data.channel_id)
        if channel:
            await channel.send(f"Error {data.error_message}")
        else:
            raise GameError("Failed to get channel.")

    """ # not used
    async def handle_command(self, ctx: commands.Context, command: str, *args):
        session = self.sessions.get(ctx.author.id)  # Changed from channel_id to author.id
        if not session:
            raise GameError("You don't have an active game")

        if command == "start":
            await session.start_game()
        else:
            pass
    """

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