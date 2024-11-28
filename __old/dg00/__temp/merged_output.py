from datetime import datetime
from datetime import datetime, timedelta
from dg00.config.config import GAME_CONFIG, ConfigLoader
from dg00.config.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message
from dg00.game.battle import BattleSystem
from dg00.game.digimon import DigimonGame
from dg00.game.evolution import EvolutionSystem
from dg00.message.bot import DigimonDiscordBot
from dg00.message.command import GameCommands
from dg00.utils.data_manager import DataManager
from discord.ext import commands
from discord.ext import commands, tasks
from pathlib import Path
from typing import Dict, Any, Optional
from typing import Optional, Dict, Any
import discord
import json
import os
import random
import sys

# Generated on 2024-11-28 22:55:52

# ===== __init__.py =====

# ===== config.py =====
import json
from pathlib import Path


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



class ConfigLoader:
    @staticmethod
    def load_token() -> str:
        """Discord 봇 토큰을 로드합니다."""
        try:
            with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'discord_token' not in data:
                    raise KeyError("token.json 파일에 'discord_token' 키가 없습니다.")
                return data['discord_token']
        except FileNotFoundError:
            raise FileNotFoundError(
                "token.json 파일을 찾을 수 없습니다.\n"
                "config/token.json 파일을 다음과 같이 생성해주세요:\n"
                '{\n    "discord_token": "YOUR_BOT_TOKEN"\n}'
            )
        except json.JSONDecodeError:
            raise ValueError("token.json 파일의 JSON 형식이 올바르지 않습니다.")

    @staticmethod
    def get_config() -> dict:
        """게임 설정을 반환합니다."""
        return GAME_CONFIG

    @staticmethod
    def get_stage_config(stage: str) -> dict:
        """특정 스테이지의 설정을 반환합니다."""
        return GAME_CONFIG['stages'].get(stage)

    @staticmethod
    def get_battle_settings() -> dict:
        """전투 관련 설정을 반환합니다."""
        return GAME_CONFIG['battle_settings']

    @staticmethod
    def get_events_config() -> dict:
        """이벤트 관련 설정을 반환합니다."""
        return GAME_CONFIG['events']

# ===== __init__.py =====

# ===== battle.py =====
import random

class BattleSystem:
    def __init__(self, config):
        self.battle_chances = config["battle_chances"]
        
    def process_battle(self, stage, count, has_cheer=False):
        if stage not in self.battle_chances:
            return None
            
        win_chance = self.battle_chances[stage]
        if has_cheer:
            win_chance *= 1.2  # 응원 효과
            
        if random.random() < win_chance:
            return {
                "result": "win",
                "new_count": int(count * 1.2)
            }
        else:
            return {
                "result": "lose",
                "new_count": int(count * 0.8)
            }
# ===== digimon.py =====
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dg00.utils.data_manager import DataManager
from dg00.config.config import GAME_CONFIG, get_next_stage, get_stage_config, get_random_message

class DigimonGame:
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self, data_manager: Optional[DataManager] = None):
        """
        DigimonGame 클래스 초기화
        
        Args:
            data_manager (Optional[DataManager]): 데이터 관리자 인스턴스
        """
        self.data_manager = data_manager or DataManager()
        self.data = self.data_manager.load_data()
    
    def get_default_player_data(self, channel_id):
        return {
            "stage": "디지타마",
            "count": 1,
            "data_absorbed": 0,
            "battles_won": 0,
            "battles_lost": 0,
            "last_cheer": None,
            "is_copying": True,
            "evolution_started": None,
            "channel_id": channel_id
        }
        
    def get_player_data(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """
        플레이어 데이터를 조회합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 플레이어 데이터 또는 None
        """
        return self.data_manager.get_player_data(user_id)
    
    def create_player(self, user_id: str | int, channel_id: id) -> Optional[Dict[str, Any]]:
        """
        새로운 플레이어를 생성합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 생성된 플레이어 데이터 또는 None (실패시)
        """
        if self.data_manager.create_player(user_id, self.get_default_player_data(channel_id)):
            self.data = self.data_manager.load_data()
            return self.data["players"].get(str(user_id))
        else:  # existing user
            return None
    
    def update_player(self, user_id: str | int, updates: Dict[str, Any]) -> bool:
        """
        플레이어 데이터를 업데이트합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            updates: 업데이트할 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if self.data_manager.update_player_data(user_id, updates):
            self.data = self.data_manager.load_data()
            return True
        return False

    def process_turn(self, user_id: str | int) -> Dict[str, Any]:
        """
        플레이어의 턴을 처리합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Dict[str, Any]: 턴 처리 결과
        """
        player_data = self.get_player_data(user_id)
        if not player_data or not player_data["is_copying"]:
            return {"status": "inactive"}

        stage_config = get_stage_config(player_data["stage"])
        if not stage_config:
            return {"status": "error", "message": "Invalid stage"}

        # 복제 및 데이터 흡수 계산
        new_count = int(player_data["count"] * (1 + stage_config["copy_rate"]))
        new_data = player_data["data_absorbed"] + stage_config["data_rate"]

        updates = {
            "count": new_count,
            "data_absorbed": new_data
        }

        # 랜덤 메시지 생성
        message = get_random_message(player_data["stage"])
        
        # 진화 체크
        evolution_status = self.check_evolution(player_data)
        if evolution_status:
            updates.update(evolution_status)

        self.update_player(user_id, updates)
        
        return {
            "status": "success",
            "count": new_count,
            "data_absorbed": new_data,
            "evolution": evolution_status,
            "message": message
        }

    def check_evolution(self, player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        진화 조건을 체크합니다.
        
        Args:
            player_data: 현재 플레이어 데이터
            
        Returns:
            Optional[Dict[str, Any]]: 진화 관련 업데이트 데이터 또는 None
        """
        if player_data["stage"] == "디아블로몬":
            return None

        stage_config = get_stage_config(player_data["stage"])
        if player_data["count"] >= stage_config["evolution_count"]:
            if player_data["evolution_started"] is None:
                return {
                    "evolution_started": datetime.now().isoformat()
                }
            
            evolution_time = datetime.fromisoformat(player_data["evolution_started"])
            time_passed = (datetime.now() - evolution_time).total_seconds()
            
            if time_passed >= stage_config["evolution_time"]:
                next_stage = get_next_stage(player_data["stage"])
                if next_stage:
                    return {
                        "stage": next_stage,
                        "count": 1,
                        "evolution_started": None
                    }
        return None

    def process_battle(self, user_id: str | int, battle_result: Dict[str, Any]) -> bool:
        """
        전투 결과를 처리합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            battle_result: 전투 결과 데이터
            
        Returns:
            bool: 처리 성공 여부
        """
        updates = {
            "count": battle_result["new_count"],
        }
        
        if battle_result["result"] == "win":
            updates["battles_won"] = self.data["players"][str(user_id)]["battles_won"] + 1
        else:
            updates["battles_lost"] = self.data["players"][str(user_id)]["battles_lost"] + 1
            updates["is_copying"] = False
            
        return self.update_player(user_id, updates)

    def apply_cheer(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """
        응원 효과를 적용합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 응원 적용 결과 또는 None
        """
        player_data = self.get_player_data(user_id)
        if not player_data:
            return None

        if not player_data["last_cheer"] or \
           datetime.now() - datetime.fromisoformat(player_data["last_cheer"]) >= timedelta(hours=1):
            self.update_player(user_id, {
                "last_cheer": datetime.now().isoformat()
            })
            return {"status": "success", "message": "응원 효과가 적용되었습니다!"}
            
        time_left = datetime.fromisoformat(player_data["last_cheer"]) + timedelta(hours=1) - datetime.now()
        return {
            "status": "cooldown",
            "message": f"다음 응원까지 {time_left.seconds // 60}분 남았습니다."
        }

    def reset_player(self, user_id: str | int) -> bool:
        """
        플레이어 데이터를 초기화합니다.
        
        Args:
            user_id: 플레이어의 Discord ID
            
        Returns:
            bool: 초기화 성공 여부
        """
        if self.data_manager.delete_player(user_id):
            return bool(self.create_player(user_id))
        return False
    
    def get_stage_config(self, stage):
        return get_stage_config(stage)
# ===== evolution.py =====
from datetime import datetime


class EvolutionSystem:
    def __init__(self, config):
        self.stages = config["stages"]
        
    def check_evolution(self, player_data):
        if player_data["stage"] == "디아블로몬":
            return None
            
        stage_config = self.stages[player_data["stage"]]
        current_count = player_data["count"]
        
        if current_count >= stage_config["evolution_count"]:
            if player_data["evolution_started"] is None:
                return {"status": "start_evolution"}
                
            evolution_time = datetime.fromisoformat(player_data["evolution_started"])
            time_passed = (datetime.now() - evolution_time).total_seconds()
            
            if time_passed >= stage_config["evolution_time"]:
                stages = list(self.stages.keys())
                current_index = stages.index(player_data["stage"])
                return {
                    "status": "evolved",
                    "new_stage": stages[current_index + 1]
                }
                
        return None
# ===== main.py =====
import discord
import sys

from dg00.config.config import GAME_CONFIG, ConfigLoader
from dg00.message.bot import DigimonDiscordBot


if __name__ == "__main__":
    try:
        TOKEN = ConfigLoader.load_token()
    except Exception as e:
        print(f"Error loading token: {str(e)}")
        sys.exit(1)

    try:
        bot = DigimonDiscordBot(GAME_CONFIG)
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Error: 디스코드 토큰이 올바르지 않습니다. token.json 파일을 확인해주세요.")
    except Exception as e:
        print(f"Error: 봇 실행 중 오류가 발생했습니다: {str(e)}")

# ===== __init__.py =====

# ===== bot.py =====
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
# ===== command.py =====
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
# ===== __init__.py =====

# ===== data_manager.py =====
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class DataManager:
    """게임 데이터를 관리하는 클래스"""
    
    DEFAULT_DATA = {
        "players": {}
    }
    
    def __init__(self, data_dir: str = 'data', filename: str = 'digimon_data.json'):
        """
        DataManager 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리 경로
            filename (str): 데이터 파일 이름
        """
        self.data_dir = Path(data_dir)
        self.filepath = self.data_dir / filename
        self._ensure_data_directory()
        
    def _ensure_data_directory(self) -> None:
        """데이터 디렉토리와 기본 파일이 존재하는지 확인하고 생성"""
        self.data_dir.mkdir(exist_ok=True)
        if not self.filepath.exists():
            self.save_data(self.DEFAULT_DATA)
            
    def load_data(self) -> Dict[str, Any]:
        """
        게임 데이터를 로드합니다.
        
        Returns:
            Dict[str, Any]: 로드된 게임 데이터
            
        Raises:
            json.JSONDecodeError: JSON 파일 형식이 잘못된 경우
        """
        try:
            if not self.filepath.exists():
                return self.DEFAULT_DATA
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict) or "players" not in data.keys():
                    return self.DEFAULT_DATA
                return data
        except json.JSONDecodeError as e:
            print(f"JSON file format is invalid: {e}")
            return self.DEFAULT_DATA
            
    def save_data(self, data: Dict[str, Any]) -> bool:
        """
        게임 데이터를 저장합니다.
        
        Args:
            data (Dict[str, Any]): 저장할 게임 데이터
            
        Returns:
            bool: 저장 성공 여부
            
        Raises:
            IOError: 파일 저장 중 오류 발생 시
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving data file: {e}")
            return False
            
    def get_player_data(self, user_id: str | int) -> Optional[Dict[str, Any]]:
        """
        특정 플레이어의 데이터를 조회합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            
        Returns:
            Optional[Dict[str, Any]]: 플레이어 데이터 또는 None
        """
        data = self.load_data()
        return data["players"].get(str(user_id))
        
    def update_player_data(self, user_id: str | int, updates: Dict[str, Any]) -> bool:
        """
        특정 플레이어의 데이터를 업데이트합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            updates (Dict[str, Any]): 업데이트할 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        data = self.load_data()
        str_user_id = str(user_id)
        
        if str_user_id not in data["players"]:
            return False
            
        data["players"][str_user_id].update(updates)
        return self.save_data(data)
        
    def create_player(self, user_id: str | int, initial_data: Dict[str, Any]) -> bool:
        """
        새로운 플레이어를 생성합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            initial_data (Dict[str, Any]): 초기 플레이어 데이터
            
        Returns:
            bool: 생성 성공 여부
        """
        data = self.load_data()
        str_user_id = str(user_id)
        
        if str_user_id in data["players"]:
            return False
        else:
            data["players"][str_user_id] = initial_data
            return self.save_data(data)
        
    def delete_player(self, user_id: str | int) -> bool:
        """
        플레이어 데이터를 삭제합니다.
        
        Args:
            user_id (str | int): 플레이어의 Discord ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        data = self.load_data()
        str_user_id = str(user_id)
        
        if str_user_id not in data["players"]:
            return False
            
        del data["players"][str_user_id]
        return self.save_data(data)
        
    def backup_data(self, backup_filename: Optional[str] = None) -> bool:
        """
        현재 데이터를 백업합니다.
        
        Args:
            backup_filename (Optional[str]): 백업 파일 이름
            
        Returns:
            bool: 백업 성공 여부
        """
        if backup_filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"digimon_data_backup_{timestamp}.json"
            
        backup_path = self.data_dir / backup_filename
        
        try:
            data = self.load_data()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
        