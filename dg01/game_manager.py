import os
import asyncio
from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.game_session import GameSession
from dg01.event_bus import EventBus
from dg01.errors import setup_logger, GameError
from dg01.digimon_config import STAGES, get_stage_config
from dg01.game_events import (
    EventType, 
    EventBase, 
    EventQuizPassNeeded,
    EventBattleWin,
    EventBattleLose,
    EventBattleItemGet,
    EventUpdateDashboard
)
from dg01.game_events import GameState
from dg01.data_manager import DataManager
from dg01.digimon_quiz import QuizHandler
from dg01.digimon_battle import BattleHandler


logger = setup_logger(__name__)


class GameManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_manager = DataManager()
        self.event_bus = EventBus()
        self.sessions: Dict[int, GameSession] = {}  # user_id: GameSession

        self.quiz_handler = QuizHandler(self.bot, self)
        self.battle_handler = BattleHandler(self.bot)

        self.setup_event_handlers()

    def setup_event_handlers(self):
        self.event_bus.subscribe(EventType.QUIZ_PASS_NEEDED, self.handle_quiz_pass_needed)
        self.event_bus.subscribe(EventType.BATTLE_WIN, self.handle_battle_win)
        self.event_bus.subscribe(EventType.BATTLE_ITEM_GET, self.handle_battle_item_get)
        self.event_bus.subscribe(EventType.BATTLE_LOSE, self.handle_battle_lose)
        self.event_bus.subscribe(EventType.UPDATE_DASHBOARD, self.handle_update_dashboard)

    # Session methods start
    async def get_session(self, user_id: int, channel_id: int) -> GameSession:
        session = self.sessions.get(user_id)
        if session:
            session.set_channel_id(channel_id=channel_id)
            return session
        else:
            digimon = await self.data_manager.get_user_data(user_id)
            session = GameSession(
                user_id=user_id,
                channel_id=channel_id,
                event_bus=self.event_bus,
                data=digimon if digimon else None
            )
            self.sessions[user_id] = session
            return session

    async def start_session(self, user_id: int, channel_id: int) -> GameSession:       
        session = await self.get_session(user_id=user_id, channel_id=channel_id)
        await session.start_game()

    async def end_session(self, user_id: int) -> bool:
        session = self.sessions.get(user_id)
        if not session:
            return False

        # 세션 정리
        await session.cleanup()

        # 활성 세션 목록에서 제거
        del self.sessions[user_id]
    
    # Session methods end

    # Quiz handles start
    async def handle_quiz_pass_needed(self, event: EventQuizPassNeeded):
        """퀴즈 이벤트를 처리하고 사용자 응답을 기다립니다."""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found")
            return
        
        await self.quiz_handler.start_quiz(
            channel=channel,
            user_id=event.user_id,
            question=event.quiz_question,
            answer=event.quiz_answer,
            timeout_callback=self.handle_quiz_timeout
        )

    async def handle_quiz_timeout(self, user_id: int) -> None:
        """
        퀴즈 타임아웃 발생 시 처리를 담당합니다.
        세션을 찾아 퀴즈 상태를 리셋하고 필요한 데이터를 업데이트합니다.
        """
        try:
            # 세션 찾기
            session = self.sessions.get(user_id)
            if not session:
                logger.warning(f"No session found for user {user_id} during quiz timeout")
                return

            # 퀴즈 실패 처리
            session.digimon.mark_quiz_failed()

            # 대시보드 업데이트
            await self.event_bus.publish(
                EventUpdateDashboard(
                    user_id=user_id,
                    channel_id=session.channel_id
                )
            )

            session.digimon.mark_quie_timeout()

        except Exception as e:
            logger.error(f"Error handling quiz timeout for user {user_id}: {e}")
    # Quiz handles end

    # Battle handles start
    async def handle_battle_win(self, event: EventBattleWin):
        """전투 승리 이벤트 처리"""
        session = self.sessions.get(event.user_id)
        if not session:
            logger.error(f"No session found for user {event.user_id}")
            return

        await self.battle_handler.handle_battle_win(
            event=event,
            battles_won=session.digimon.battles_won,
            battles_lost=session.digimon.battles_lost
        )

    async def handle_battle_item_get(self, event: EventBattleItemGet):
        """전투 아이템 획득 이벤트 처리"""
        await self.battle_handler.handle_battle_item_get(event)

    async def handle_battle_lose(self, event: EventBattleLose):
        """전투 패배 이벤트 처리"""
        session = self.sessions.get(event.user_id)
        if not session:
            logger.error(f"No session found for user {event.user_id}")
            return

        await self.battle_handler.handle_battle_lose(
            event=event,
            battles_won=session.digimon.battles_won,
            battles_lost=session.digimon.battles_lost,
            remaining_count=session.digimon.count
        )
        
    # Battle handles end

 
    async def handle_update_dashboard(self, event: EventUpdateDashboard, update_img=False):
        """Update the existing dashboard message with new data"""
        session = await self.get_session(user_id=event.user_id, channel_id=event.channel_id)
        if not session.dashboard_message:
            return

        try:
            channel = self.bot.get_channel(event.channel_id)
            if not channel:
                logger.error(f"Channel {event.channel_id} not found")
                return

            # Create new embed with updated data
            main_embed, info_embed = await self.create_dashboard_embeds(
                user_id=event.user_id,
                user_name=session.user_name,
                channel_id=event.channel_id,
                update_img=update_img
            )
            
            # 이미지 파일이 있는 경우와 없는 경우를 구분하여 처리
            if update_img and session.current_image_file:
                await session.dashboard_message.edit(
                    embeds=[main_embed, info_embed],
                    attachments=[session.current_image_file]
                )
            else:
                await session.dashboard_message.edit(
                    embeds=[main_embed, info_embed]
                )

        except discord.NotFound:
            # Message was deleted
            self.dashboard_message = None
        except discord.HTTPException as e:
            logger.error(f"Failed to update dashboard: {e}")
        except Exception as e:
            logger.error(f"Dashboard update error: {e}")

    async def create_dashboard_embeds(self, user_id, user_name, channel_id, update_img=False):
        """Create dashboard embeds with current data"""
        
        session = await self.get_session(user_id=user_id, channel_id=channel_id)
        session.set_user_name(user_name)
        stage_config = get_stage_config(session.digimon.stage_idx)
        
        # Main status embed
        title = f"🎮 {user_name}의 디지몬 대시보드" if user_name else "디지몬 대시보드"
        main_embed = discord.Embed(
            title=title,
            description=f"현재 스테이지: {STAGES[session.digimon.stage_idx]}",
            color=discord.Color.blue()
        )

        # 이미지 추가
        if update_img:
            image_path = stage_config.get('image_path')
            if image_path and os.path.exists(image_path):
                main_embed.set_image(url="attachment://digimon.png")

        
        # Progress section
        progress_bar = self.create_progress_bar(
            current=session.digimon.count,
            max=stage_config["evolution_count"],
            length=10
        )
        
        main_embed.add_field(
            name="📊 진화 진행도",
            value=f"```\n{progress_bar}\n"
                  f"{session.digimon.count:,} / {stage_config['evolution_count']:,} "
                  f"({session.digimon.count/stage_config['evolution_count']*100:.1f}%)\n```",
            inline=False
        )
        
        
        # Stats section
        main_embed.add_field(
            name="📈 기본 정보",
            value=f"```\n"
                f"복제 속도: {stage_config['copy_rate']}/초\n"
                f"총 개체 수: {session.digimon.count:,}\n"
                f"데이터량: {session.digimon.count/1024:.1f} GB\n```",
            inline=True
        )
        
        # Battle stats section
        total_battles = session.digimon.battles_won + session.digimon.battles_lost
        win_rate = (session.digimon.battles_won / total_battles * 100) if total_battles > 0 else 0
        
        main_embed.add_field(
            name="⚔️ 전투 기록",
            value=f"```\n"
                f"승리: {session.digimon.battles_won}\n"
                f"패배: {session.digimon.battles_lost}\n"
                f"승률: {win_rate:.1f}%\n```",
            inline=True
        )
        
        # System status section
        status_indicators = {
            "복제 상태": "🟢 진행중" if session.digimon.is_copying else "🔴 중단됨~~  `!치료` 해줘 ㅠㅠ",
            "퀴즈 대기": "⏳ 대기중" if session.digimon.quiz_pass_needed else "✅ 없음"
        }
        
        status_text = "\n".join(f"{k}: {v}" for k, v in status_indicators.items())
        main_embed.add_field(
            name="🔧 시스템 상태",
            value=f"```\n{status_text}\n```",
            inline=False
        )
    
        
        # Active effects section
        if session.digimon.last_cheer:
            cheer_time = datetime.fromisoformat(session.digimon.last_cheer)
            time_left = (cheer_time + timedelta(hours=1) - datetime.now()).total_seconds() / 60
            if time_left > 0:
                main_embed.add_field(
                    name="🌟 활성화된 효과",
                    value=f"응원 효과: {time_left:.0f}분 남음",
                    inline=False
                )

        # Footer with last update time
        main_embed.set_footer(text=f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Add stage specific info
        if 'special_move' in stage_config:
            info_embed = discord.Embed(
                title="📖 스테이지 정보",
                color=discord.Color.gold()
            )
            info_embed.add_field(
                name="필살기",
                value=stage_config['special_move'],
                inline=False
            )
            info_embed.add_field(
                name="설명",
                value=stage_config['description'],
                inline=False
            )
    
        return main_embed, info_embed

    def create_progress_bar(self, current: int, max: int, length: int = 10) -> str:
        """Create a text-based progress bar"""
        filled = int((current / max) * length)
        return f"[{'█' * filled}{'░' * (length - filled)}]"

    
    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ", "ㅆㄸㅆㄸ"])
    async def first_evolve(self, ctx: commands.Context):
        """첫 진화 명령어"""
        try:
            session = await self.get_session(user_id=ctx.author.id, channel_id=ctx.channel.id)

            if session.digimon.stage_idx == min(STAGES.keys()) and session.digimon.count == 0:
                await ctx.send(f"짜잔! {ctx.author.name}의 디지타마가 태어났어! 🥚✨")
            else:
                await ctx.send(f"어라? {ctx.author.name} 지금 이미 디지타마를 돌보고 있잖아요! 🥚")

            await self.start_session(user_id=ctx.author.id, channel_id=ctx.channel.id)
        except ValueError:
            raise GameError("oh3?")
        
    @commands.command(name="현황")
    async def status(self, ctx: commands.Context):
        """현재 디지몬의 상태를 확인합니다."""
        session = await self.get_session(user_id=ctx.author.id, channel_id=ctx.channel.id)

        if session.state == GameState.WAITING:
            await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다. `!쓰담쓰담`으로 시작하세요!")
            return
        
        stage_config = get_stage_config(session.digimon.stage_idx)
        stage_idx, stage_name = stage_config["stage_idx"], STAGES[session.digimon.stage_idx]
        
        # 이미지 파일 확인
        image_path = stage_config.get('image_path')
        if not image_path or not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}")
            image_file = None
        else:
            image_file = discord.File(image_path, filename="digimon.png")

        # 임베드 생성
        status_embed = discord.Embed(
            title=f"🎮 {stage_name}",
            description=stage_config['description'],
            color=discord.Color.blue()
        )
        
        if image_file:
            status_embed.set_thumbnail(url="attachment://digimon.png")
        
        # 기본 정보
        status_embed.add_field(
            name="📊 현재 상태",
            value=f"```"
                  f"현재 개체 수: {session.digimon.count:,} 개체\n"
                  f"흡수한 데이터: {session.digimon.count / 1024:.1f} GB\n"
                  f"전적: {session.digimon.battles_won}승 {session.digimon.battles_lost}패"
                  f"```",
            inline=False
        )
        
        # 필살기 정보
        if 'special_move' in stage_config:
            status_embed.add_field(
                name="⚔️ 필살기",
                value=f"{stage_config['special_move']}",
                inline=True
            )
        
        # 복제 상태 표시
        if not session.digimon.is_copying:
            status_embed.add_field(
                name="⚠️ 주의",
                value="현재 복제가 중단된 상태입니다. `!치료` 명령어로 복제를 재개하세요.",
                inline=False
            )
            status_embed.color = discord.Color.red()
        
        # 진화 정보 표시
        if stage_idx != max(STAGES.keys()):
            remaining = stage_config["evolution_count"] - session.digimon.count
            status_embed.add_field(
                name="🔄 진화 정보",
                value=f"다음 진화까지 {remaining:,} 개체 필요",
                inline=False
            )

        # 임베드 전송
        if image_file:
            await ctx.send(file=image_file, embed=status_embed)
        else:
            await ctx.send(embed=status_embed)

    @commands.command(name="응원")
    async def cheer(self, ctx):
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx: commands.Context):
        """복제가 중단된 디지몬의 복제를 재개합니다."""
        try:
            session = await self.get_session(
                user_id=ctx.author.id, 
                channel_id=ctx.channel.id
            )
            
            if session.state == GameState.WAITING:
                await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다. `!쓰담쓰담`으로 시작하세요!")
                return

            if session.digimon.quiz_pass_needed:
                embed = discord.Embed(
                    title="❌ 치료 실패",
                    description="진화 퀴즈를 통과해야 복제를 재개할 수 있습니다!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            if session.digimon.is_copying:
                embed = discord.Embed(
                    title="ℹ️ 치료 불필요",
                    description="이미 정상적으로 복제가 진행 중입니다!",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
                return

            # 복제 재개
            session.digimon.start_copying()
            
            # 성공 메시지 전송
            embed = discord.Embed(
                title="✨ 치료 성공",
                description="복제가 다시 시작되었습니다!",
                color=discord.Color.green()
            )
            
            # 현재 스테이지 정보 추가
            embed.add_field(
                name="📊 현재 상태",
                value=f"스테이지: {STAGES[session.digimon.stage_idx]}\n"
                    f"현재 개체 수: {session.digimon.count:,}",
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Cure command error: {e}")
            await ctx.send("치료 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

    @commands.command(name='방생')
    async def end_session(self, ctx: commands.Context):
        """게임 종료 명령어"""
        success = await self.end_session(ctx.author.id, ctx.channel.id)

        if success:
            await ctx.send(f"{ctx.author.name}! 너와 작별하다니 하니 가슴이 아프다... 😢")
        else:
            await ctx.send(f"어라? {ctx.author.name}! 아직 네 디지몬이 없는데 뭘 보내려는 거야? 🤔")

    @commands.command(name='대시보드', aliases=["보드", "ㅂㄷ", "ㄷㅅㅂㄷ"])
    async def dashboard(self, ctx: commands.Context):
        """Create or update the game dashboard"""
        session = await self.get_session(ctx.author.id, ctx.channel.id)
        if session.state == GameState.WAITING:
            await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다.")
            return

        try:

            # 이미지 파일 준비 
            stage_config = get_stage_config(session.digimon.stage_idx)
            image_path = stage_config.get('image_path')
            file = discord.File(image_path, filename="digimon.png") if image_path and os.path.exists(image_path) else None

            # Create new dashboard embeds
            main_embed, info_embed = await self.create_dashboard_embeds(
                user_id=ctx.author.id,
                user_name=ctx.author.name,
                channel_id=ctx.channel.id,
                update_img=bool(file)
            )

            # 파일과 함께 메시지 전송
            message = await ctx.send(file=file, embeds=[main_embed, info_embed]) if file else await ctx.send(embeds=[main_embed, info_embed])
            session.set_dashboard_message(message)
            session.last_dashboard_update = asyncio.get_running_loop().time()

        except Exception as e:
            logger.error(f"Dashboard command error: {e}")
            await ctx.send("대시보드 생성 중 오류가 발생했습니다.")
