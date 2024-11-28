import os
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands

from dg01.errors import GameError
from dg01.digimon_config import get_stage_config, EVOLUTION_ORDER, STAGES
from dg01.game_events import EventType


class GameCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="디지스타트", aliases=["ㄱ", "ㄱㄱ", "ㄱㄱㄱ"])
    async def start(self, ctx: commands.Context):
        """게임 시작 명령어"""
        try:
            start_event = await self.bot.game_manager.start_session(ctx.author.id, ctx.channel.id)
            if start_event == EventType.CREATE_PLAYER:
                await ctx.send(f"짜잔! {ctx.author.name}의 디지타마가 태어났어! 🥚✨")
            elif start_event == EventType.GAME_STARTED:
                await ctx.send(f"어라? {ctx.author.name} 지금 이미 디지타마를 돌보고 있잖아요! 🥚")
            else:
                raise GameError("oh?")
        except ValueError:
            raise GameError("oh?")
    
    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ", "tete"])
    async def first_evolve(self, ctx: commands.Context):
        """첫 진화 명령어"""
        try:
            player_data = await self.bot.game_manager.data_manager.get_or_create_user_data(ctx.author.id)
            if player_data["stage_idx"] == min(STAGES.keys()):
                player_data["stage_idx"] += 1
                print(f"{player_data=}")
                success = await self.bot.game_manager.data_manager.update_user_data(ctx.author.id, player_data)
                # success = 1
                if success:
                    await ctx.send(f"짜잔! {ctx.author.name}의 디지타마가 부화했습니다! 🥚✨")
                else:
                    await ctx.send(f"어라? {ctx.author.name} 부화에 실패했어.🥚")
            else:
                await ctx.send(f"{ctx.author.name} 너의 디지타마는 이미 부화했어")
        except ValueError:
            raise GameError("oh?")
        

    @commands.command(name="현황")
    async def status(self, ctx: commands.Context):
        """현재 디지몬의 상태를 확인합니다."""
        player_data = await self.bot.game_manager.data_manager.get_or_create_user_data(ctx.author.id)
        print(f"=== {player_data} ===")
        
        if player_data is None:
            await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다. `!쓰담쓰담`으로 시작하세요!")
            return
        
        stage_config = get_stage_config(player_data['stage_idx'])
        stage_idx, stage_name = stage_config["stage_idx"], STAGES[stage_config["stage_idx"]]
        
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
                  f"현재 개체 수: {player_data['count']:,} 개체\n"
                  f"흡수한 데이터: {player_data['count'] / 1024:.1f} GB\n"
                  f"전적: {player_data['battles_won']}승 {player_data['battles_lost']}패"
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
        if not player_data["is_copying"]:
            status_embed.add_field(
                name="⚠️ 주의",
                value="현재 복제가 중단된 상태입니다. `!치료` 명령어로 복제를 재개하세요.",
                inline=False
            )
            status_embed.color = discord.Color.red()
        
        # 진화 정보 표시
        if stage_idx != max(STAGES.keys()):
            remaining = stage_config["evolution_count"] - player_data["count"]
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
        await self.bot.game_manager.data_manager.update_user_data(user_id=ctx.author.id, data={"last_cheer": (datetime.now(timezone.utc) + timedelta(hours=9)).isoformat()})
        await ctx.send('응원 응원')

    @commands.command(name="치료")
    async def cure(self, ctx):
        await self.bot.game_manager.data_manager.update_user_data(user_id=ctx.author.id, data={"is_copying": 1, "channel_id": ctx.channel.id})
        await ctx.send('치료 치료')

    @commands.command(name='방생')
    async def end_game(self, ctx: commands.Context):
        """게임 종료 명령어"""
        success = await self.bot.game_manager.end_game(ctx.author.id, ctx.channel.id)

        if success:
            await ctx.send(f"{ctx.author.name}! 너와 작별하다니 하니 가슴이 아프다... 😢")
        else:
            await ctx.send(f"어라? {ctx.author.name}! 아직 네 디지몬이 없는데 뭘 보내려는 거야? 🤔")

    async def send_status(self, user_id: str, channel_id: int, event_type: str = None):
        """현황을 출력하는 함수"""
        channel = self.get_channel(channel_id)
        if not channel:
            return

        player_data = self.game.get_player_data(user_id)
        if not player_data:
            return

        stage_config = self.game_config["stages"][player_data['stage']]
        
        # 이미지 파일 확인
        image_path = stage_config.get('image_path')
        image_file = discord.File(image_path, filename="digimon.png") if image_path and os.path.exists(image_path) else None
        
        # 이벤트 타입에 따른 임베드 색상과 제목
        if event_type is None:
            color = discord.Color.white()
            title = f"📊 지금은! - {player_data['stage']}"
        elif event_type == "evolution":
            color = discord.Color.gold()
            title = f"🌟 진화! - {player_data['stage']}"
        elif event_type == "battle_win":
            color = discord.Color.green()
            title = f"⚔️ 전투 승리! - {player_data['stage']}"
        elif event_type == "battle_lose":
            color = discord.Color.red()
            title = f"💔 전투 패배! - {player_data['stage']}"
        else:
            color = discord.Color.blue()
            title = f"🎮 {player_data['stage']}"

        status_embed = discord.Embed(
            title=title,
            description=stage_config['description'],
            color=color
        )
        
        if image_file:
            status_embed.set_thumbnail(url="attachment://digimon.png")
        
        status_embed.add_field(
            name="📊 현재 상태",
            value=f"```"
                  f"현재 개체 수: {player_data['count']:,} 개체\n"
                  f"흡수한 데이터: {player_data['count'] / 1024:.1f} GB\n"
                  f"전적: {player_data['battles_won']}승 {player_data['battles_lost']}패"
                  f"```",
            inline=False
        )
        
        if 'special_move' in stage_config:
            status_embed.add_field(
                name="⚔️ 필살기",
                value=f"{stage_config['special_move']}",
                inline=True
            )
        
        if not player_data["is_copying"]:
            status_embed.add_field(
                name="⚠️ 주의",
                value="현재 복제가 중단된 상태입니다. `!치료` 명령어로 복제를 재개하세요.",
                inline=False
            )
        
        if player_data['stage'] != "디아블로몬":
            remaining = stage_config["evolution_count"] - player_data["count"]
            status_embed.add_field(
                name="🔄 진화 정보",
                value=f"다음 진화까지 {remaining:,} 개체 필요",
                inline=False
            )

        status_embed.set_footer(text=f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if image_file:
            await channel.send(file=image_file, embed=status_embed)
        else:
            await channel.send(embed=status_embed)