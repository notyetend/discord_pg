import os
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from dg00.utils.data_manager import DataManager
from dg00.game.digimon import DigimonGame
from dg00.message.command import GameCommands
from dg00.game.battle import BattleSystem
from dg00.game.evolution import EvolutionSystem


class DigimonDiscordBot(commands.Bot):
    def __init__(self, game_config):

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=commands.DefaultHelpCommand(
                no_category='Commands'
            )
        )

        self.game_config = game_config
        self.data_manager = DataManager()
        self.game = DigimonGame(self.data_manager)
        self.battle_system = BattleSystem(game_config)
        self.evolution_system = EvolutionSystem(game_config)
        self.last_status_time = {}

    async def setup_hook(self):
        """봇 시작시 실행될 코드"""
        await self.add_cog(GameCommands(self, self.game))
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_ready(self):
        """봇이 준비되었을 때 실행될 코드"""
        print(f'{self.user} has connected to Discord!')
        print('Bot is ready to play Digimon War Game!')
        
        # 게임 업데이트 루프 시작
        update_game.start(self)

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
        if event_type == "evolution":
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
                  f"흡수한 데이터: {player_data['data_absorbed'] / 1024:.1f} GB\n"
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



@tasks.loop(seconds=1)
async def update_game(bot: DigimonDiscordBot):
    current_time = datetime.now()

    for user_id, player in bot.game.data["players"].copy().items():
        if not player["is_copying"]:
            continue
        
        stage_config = bot.game_config["stages"][player["stage"]]
        
        # 복제 및 데이터 흡수
        new_count = int(player["count"] * (1 + stage_config["copy_rate"]))
        new_data = player["data_absorbed"] + stage_config["data_rate"]
        
        # 1분마다 현황 출력
        last_time = bot.last_status_time.get(user_id, current_time - timedelta(minutes=1))
        if (current_time - last_time).total_seconds() >= 60:
            channel_id = player.get("channel_id")  # 마지막으로 명령어를 사용한 채널 ID
            if channel_id:
                await bot.send_status(user_id, channel_id)
                bot.last_status_time[user_id] = current_time

        # 진화 체크
        evolution_result = bot.evolution_system.check_evolution(player)
        if evolution_result:
            if evolution_result["status"] == "start_evolution":
                bot.game.update_player(user_id, {
                    "evolution_started": datetime.now().isoformat()
                })
            elif evolution_result["status"] == "evolved":
                bot.game.update_player(user_id, {
                    "stage": evolution_result["new_stage"],
                    "count": 1,
                    "evolution_started": None
                })

                # 진화 시 현황 출력
                if channel_id := player.get("channel_id"):
                    event_type = "battle_lose"
                    await bot.send_status(user_id, channel_id, event_type)
        
        # 랜덤 전투
        if random.random() < bot.game_config["battle_settings"]["battle_chance"]:
            battle_result = bot.battle_system.process_battle(
                player["stage"], 
                new_count,
                player["last_cheer"] is not None
            )
            
            if battle_result:
                updates = {
                    "count": battle_result["new_count"],
                    "data_absorbed": new_data
                }
                
                if battle_result["result"] == "win":
                    updates["battles_won"] = player["battles_won"] + 1
                    event_type = "battle_win"
                else:
                    updates["battles_lost"] = player["battles_lost"] + 1
                    updates["is_copying"] = False
                    event_type = "battle_lose"
                
                bot.game.update_player(user_id, updates)

                if channel_id := player.get("channel_id"):
                    await bot.send_status(user_id, channel_id, event_type)

                continue
        
        bot.game.update_player(user_id, {
            "count": new_count,
            "data_absorbed": new_data
        })