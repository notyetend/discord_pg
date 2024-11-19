from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.session import GameSession
from dg01.events import EventBus
from dg01.errors import GameError
from dg01.states import GameType
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