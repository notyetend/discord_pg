import os
from discord.ext import commands
import discord


class GameCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, game):
        self.bot = bot
        self.game = game

    # Cog가 로드되었을 때 확인용 출력
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"GameCommands Cog is ready!")

    @commands.command(name="쓰담쓰담", aliases=["ㅅㄷㅅㄷ", "ㅆㄷㅆㄷ"])
    async def start_game(self, ctx: commands.Context):
        """게임을 시작하고 디지타마를 부화시킵니다."""
        player_data = self.game.get_player_data(ctx.author.id)
        
        if player_data is None:
            result = self.game.create_player(ctx.author.id, ctx.channel.id)
            if result:
                await ctx.send(f"{ctx.author.mention}님의 디지타마가 부화했습니다! 🥚")
            else:
                await ctx.send(f"{ctx.author.mention}님의 게임 생성 중 오류가 발생했습니다.")
        else:
            self.game.update_player(ctx.author.id, {"channel_id": ctx.channel.id})
            await ctx.send(f"{ctx.author.mention}님은 이미 게임을 진행 중입니다.")

    @commands.command(name="현황")
    async def status(self, ctx: commands.Context):
        """현재 디지몬의 상태를 확인합니다."""
        player_data = self.game.get_player_data(ctx.author.id)
        
        if player_data is None:
            await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다. `!쓰담쓰담`으로 시작하세요!")
            return
        
        stage_config = self.game.get_stage_config(player_data['stage'])
        
        # 이미지 파일 확인
        image_path = stage_config.get('image_path')
        if not image_path or not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}")
            image_file = None
        else:
            image_file = discord.File(image_path, filename="digimon.png")

        # 임베드 생성
        status_embed = discord.Embed(
            title=f"🎮 {player_data['stage']}",
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
                  f"흡수한 데이터: {player_data['data_absorbed'] / 1024:.1f} GB\n"
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
        if player_data['stage'] != "디아블로몬":
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

    @commands.command(name="치료")
    async def heal(self, ctx: commands.Context):
        """전투에서 패배로 중단된 복제를 재개합니다."""
        player_data = self.game.get_player_data(ctx.author.id)
        
        if player_data is None:
            await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다.")
            return
        
        if player_data["is_copying"]:
            await ctx.send(f"{ctx.author.mention}님의 디지몬은 이미 정상적으로 복제 중입니다.")
            return
        
        if self.game.update_player(ctx.author.id, {"is_copying": True}):
            await ctx.send(f"💊 {ctx.author.mention}님의 디지몬이 회복되어 다시 복제를 시작합니다!")
        else:
            await ctx.send(f"{ctx.author.mention}님의 디지몬 치료 중 오류가 발생했습니다.")

    @commands.command(name="응원")
    async def cheer(self, ctx: commands.Context):
        """디지몬을 응원하여 1시간 동안 전투 승률을 높입니다."""
        result = self.game.apply_cheer(ctx.author.id)
        
        if result is None:
            await ctx.send(f"{ctx.author.mention}님은 아직 게임을 시작하지 않았습니다.")
            return
        
        await ctx.send(f"{ctx.author.mention}님, {result['message']}")

    @start_game.error
    @status.error
    @heal.error
    @cheer.error
    async def command_error(self, ctx: commands.Context, error: Exception):
        """명령어 실행 중 발생하는 오류를 처리합니다."""
        if isinstance(error, commands.CommandError):
            await ctx.send(f"명령어 실행 중 오류가 발생했습니다: {str(error)}")
        else:
            print(f"Unexpected error: {error}")
            await ctx.send("예기치 않은 오류가 발생했습니다. 나중에 다시 시도해주세요.")