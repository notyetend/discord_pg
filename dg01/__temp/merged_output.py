from abc import ABC
from dataclasses import dataclass
from dataclasses import dataclass, field
from dataclasses import field
from datetime import datetime
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from datetime import datetime, timezone, timedelta
from dg01.data_manager import DataManager
from dg01.digimon_cog import GameCommandsCog
from dg01.digimon_config import STAGES
from dg01.digimon_config import STAGES, STAGE_CONFIG
from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx
from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx, get_stage_config, get_battle_chance, get_random_message, get_evolution_quiz
from dg01.digimon_config import get_stage_config, EVOLUTION_ORDER, STAGES
from dg01.digimon_data import DigimonDataFields
from dg01.digimon_logic import DigimonLogic
from dg01.errors import GameError
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError
from dg01.event_bus import EventBus
from dg01.game_events import EventType
from dg01.game_events import EventType, EventBase
from dg01.game_events import EventType, EventBase, EventGameStarted, EventGameCleanup, EventError, EventUpdatePlayer, GameState
from dg01.game_events import EventType, EventGameStarted, EventError
from dg01.game_events import EventType, EventGameStarted, EventGameCleanup, EventError, EventUpdatePlayer
from dg01.game_events import EventType, EventUpdatePlayer
from dg01.game_events import GameState, EventType, EventGameStarted, EventError, EventGameCleanup
from dg01.game_events import GameState, EventType, EventGameStarted, EventGameCleanup, EventError
from dg01.game_manager import GameManager
from dg01.game_session import GameSession
from discord.ext import commands
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict
from typing import Dict, List
from typing import Dict, Type
from typing import Optional
from typing import Optional, Dict, Any, List
from typing import Optional, Dict, Any, List, NamedTuple
from typing import TypeVar, Generic
from unittest.mock import Mock, AsyncMock
from unittest.mock import Mock, AsyncMock, patch
import aiosqlite
import asyncio
import discord
import json
import logging
import os
import pandas as pd
import pytest
import random
import sqlite3
import sys
import traceback

# Generated on 2024-11-28 22:58:25

# ===== data_manager.py =====
import os
import sqlite3
import aiosqlite
from typing import Optional, Dict, Any, List
from dg01.digimon_data import DigimonDataFields
from dg01.errors import setup_logger, GameError


logger = setup_logger(__name__)


class DataManager:
    def __init__(self, db_path: str = '__game_data/game.db', table_name: str = 'user_data'):
        """
        GameDataManager 초기화
        
        Args:
            db_path (str): 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.table_name = table_name
        self.fields = DigimonDataFields()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    @property
    def create_table_sql(self) -> str:
        """테이블 생성 SQL 쿼리 생성"""
        fields = []
        for field_name, field_info in self.fields.__dataclass_fields__.items():
            metadata = field_info.metadata
            field_def = [
                field_name,
                metadata.get("type", "TEXT")
            ]
            
            if metadata.get("primary_key"):
                field_def.append("PRIMARY KEY")
            if not metadata.get("nullable", True):
                field_def.append("NOT NULL")
            if "default" in metadata:
                default_value = metadata["default"]
                if isinstance(default_value, str):
                    field_def.append(f"DEFAULT '{default_value}'")
                else:
                    field_def.append(f"DEFAULT {default_value}")
                
            fields.append(" ".join(field_def))
            
        return f"""CREATE TABLE IF NOT EXISTS {self.table_name} (\n\t{'\n\t, '.join(fields)}\n)"""

    @property
    def default_user_data(self) -> Dict[str, Any]:
        """기본 사용자 데이터"""
        return {
            field_name: field_info.default
            for field_name, field_info in self.fields.__dataclass_fields__.items()
            if "default" in field_info.metadata
        }

    @property
    def columns(self) -> List[str]:
        """컬럼 목록"""
        return list(self.fields.__dataclass_fields__.keys())

    def _init_db(self) -> None:
        """데이터베이스와 테이블을 초기화합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(self.create_table_sql)
        except sqlite3.Error as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise

    async def get_or_create_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 게임 데이터를 불러옵니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 게임 데이터
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                if row is None:
                    # 새 사용자 데이터 생성
                    user_data = self.default_user_data.copy()
                    
                    placeholders = ", ".join(["?"] * len(self.columns))
                    values = [
                        user_id,
                        *[user_data.get(col) for col in self.columns[1:]]
                    ]
                    
                    await db.execute(
                        f"""
                        INSERT INTO {self.table_name} (
                            {", ".join(self.columns)}
                        ) VALUES ({placeholders})
                        """,
                        values
                    )
                    await db.commit()

                    async with db.execute(
                        f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                        (user_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row is None:
                            raise GameError("Fail to fetch data.")
                else:
                    pass
                
                return {
                    self.columns[i]: (
                        None if row[i] == ''
                        else row[i]
                    )
                    for i in range(len(self.columns))
                }
                
            except Exception as e:
                logger.error(f"데이터 로드 실패 (user_id: {user_id}): {e}")
                raise


    async def create_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 게임 데이터를 불러옵니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 게임 데이터
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                
                assert row is None
                
                # 새 사용자 데이터 생성
                user_data = self.default_user_data.copy()
                
                placeholders = ", ".join(["?"] * len(self.columns))
                values = [
                    user_id,
                    *[user_data.get(col) for col in self.columns[1:]]
                ]
                
                await db.execute(
                    f"""
                    INSERT INTO {self.table_name} (
                        {", ".join(self.columns)}
                    ) VALUES ({placeholders})
                    """,
                    values
                )
                await db.commit()

                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise GameError("Fail to fetch data.")
                    
                return {
                    self.columns[i]: (
                        None if row[i] == ''
                        else row[i]
                    )
                    for i in range(len(self.columns))
                }
                
            except Exception as e:
                logger.error(f"데이터 로드 실패 (user_id: {user_id}): {e}")
                raise

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 게임 데이터를 불러옵니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 게임 데이터
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                if row is None:
                    return None
                else:
                    return {
                        self.columns[i]: (
                            None if row[i] == ''
                            else row[i]
                        )
                        for i in range(len(self.columns))
                    }
                
            except Exception as e:
                logger.error(f"데이터 로드 실패 (user_id: {user_id}): {e}")
                raise

    async def update_user_data(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        사용자의 게임 데이터를 저장합니다.
        
        Args:
            user_id (int): 사용자 ID
            data (Dict[str, Any]): 저장할 게임 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        if not isinstance(data, dict):
            logger.error(f"잘못된 데이터 형식 (user_id: {user_id}): {type(data)}")
            return False
        
        try:
            update_fields = [c for c in self.columns if c in data.keys() and c != "user_id"]
            if len(update_fields) == 0:
                return False
                        
            update_expr = [f"{col} = :{col}" for col in update_fields]
            update_data = {k: v for k, v in data.items() if k in update_fields}
            update_query = f"""UPDATE user_data SET {', '.join(update_expr)} WHERE user_id = :user_id"""
            update_params = {**{col: update_data.get(col) for col in update_fields}, 'user_id': user_id}
            print(f"{update_query=}")
            print(f"{update_data=}")
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(sql=update_query, parameters=update_params)
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"데이터 저장 실패 (user_id: {user_id}): {e}")
            return False


    async def get_all_user_data(self) -> List[Dict[str, Any]]:
        """
        모든 사용자의 게임 데이터를 조회합니다.
        
        Returns:
            List[Dict[str, Any]]: 전체 사용자 게임 데이터 목록
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name}'
                ) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            self.columns[i]: (
                                None if row[i] == ''
                                else row[i]
                            )
                            for i in range(len(self.columns))
                        }
                        for row in rows
                    ]
                    
            except Exception as e:
                logger.error(f"전체 데이터 로드 실패: {e}")
                raise

# ===== digimon_cog.py =====
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
# ===== digimon_config.py =====
import pandas as pd

STAGES = {  # stage_idx: stage_name
    0: "디지타마",
    1: "쿠라몬",
    2: "츠메몬",
    3: "케라몬",
    4: "크리사리몬",
    5: "인펠몬",
    6: "디아블로몬"
}

STAGE_CONFIG = [
    {
        "stage_idx": 0,
        "evolution_time": 30,  # 예상 진화 시간(초)
        "evolution_count": 100,  # MB
        "copy_rate": 3,  # MB, 초당 증식
        "description": "부화를 기다리는 디지타마입니다. !쓰담쓰담으로 부화시켜주세요.",
        "image_path": "assets/digitama.webp",
        "battle_chance": 1,
        "random_messages": [],
        "evolution_quiz": [],
    },
    {
        "stage_idx": 1,
        "evolution_time": 7 * 60 + 30,
        "evolution_count": 10_000,
        "copy_rate": 22,
        "description": "컴퓨터 네트워크상에 갑자기 출연한 정체불명의 디지몬. 네트워크에서 병원균처럼 번식해 가벼운 네트워크 장애를 일으킵니다.",
        "special_move": "글레어 아이",
        "image_path": "assets/kuramon.webp",
        "battle_chance": 1.0,  # 튜토리얼이므로 100% 승리
        "random_messages": [
            "데이터 맛있어요~",
            "더 많이 복제되고 싶어!"
        ],
        "evolution_quiz": [
            {
                "question": "처음으로 등장한 컴퓨터 바이러스의 이름은?",
                "answer": "크리퍼",
                "hint": "1971년에 만들어진 이 바이러스는 'Creeper'라는 메시지를 출력했습니다."
            },
        ],
    },
    {
        "stage_idx": 2,
        "evolution_time": 60 * 60,
        "evolution_count": 1_000_000,  # 1TB
        "copy_rate": 278,
        "description": "쿠라몬이 더 진화한 유년기 디지몬. 촉수 끝이 갈고리발톱처럼 돼서 더 포악해졌습니다.",
        "special_move": "네일 스크래치",
        "image_path": "assets/tsumemon.webp",
        "battle_chance": 0.8,  # 80% 승률
        "random_messages": [
            "네트워크가 약해빠졌네?",
            "더 강한 시스템을 찾아보자!"
        ],
        "evolution_quiz": [
            {
                "question": "최초의 웜 바이러스의 이름은?",
                "answer": "모리스 웜",
                "hint": "1988년 로버트 모리스가 만든 이 악성코드는 인터넷 역사상 최초의 웜입니다."
            },
        ],
    },
    {
        "stage_idx": 3,
        "evolution_time": 12 * 60 * 60,
        "evolution_count": 1_000_000_000,  # 1PB
        "copy_rate": 23_148,
        "description": "츠메몬이 진화한 성장기 디지몬. 매우 활기찬 성격으로 파괴 행위는 놀이의 일환이라고 생각합니다.",
        "special_move": "찰싹 때리기",
        "image_path": "assets/kuramon.webp",
        "battle_chance": 0.6,  # 60% 승률
        "random_messages": [
            "파괴는 정말 재미있어!",
            "이 정도 보안은 찰싹이야!"
        ],
        "evolution_quiz": [
            {
                "question": "램섬웨어의 대표적인 공격 방식은?",
                "answer": "암호화",
                "hint": "피해자의 파일을 이것을 통해 접근할 수 없게 만듭니다."
            },
        ],
    },
    {
        "stage_idx": 4,
        "evolution_time": 24 * 60 * 60,
        "evolution_count": 1_000_000_000_000,  # 1EB
        "copy_rate": 11_574_074,  # 1초당 3.5배로 복제
        "description": "번데기의 모습을 한 성숙기 디지몬. 이동은 전혀 할 수 없지만 단단한 외피로 보호됩니다.",
        "special_move": "데이터 파괴",
        "image_path": "assets/chrysalimon.webp",
        "battle_chance": 0.5,  # 50% 승률
        "random_messages": [
            "더 강한 힘을 원해...",
            "아무도 날 막을 수 없어"
        ],
        "evolution_quiz": [
            {
                "question": "DDoS 공격의 풀네임은?",
                "answer": "분산 서비스 거부 공격",
                "hint": "여러 곳에서 동시에 서버를 공격하는 방식입니다."
            },
        ],
    },
    {
        "stage_idx": 5,
        "evolution_time": 48 * 60 * 60,
        "evolution_count": 1_000_000_000_000_000,  # 1ZB
        "copy_rate": 578_703_703,
        "description": "손발이 긴 거미의 모습을 한 완전체 디지몬. 강력한 보안과 상관없이 모든 네트워크에 침입할 수 있습니다.",
        "special_move": "네트워크수류탄",
        "image_path": "assets/infermon.webp",
        "battle_chance": 0.4,  # 40% 승률
        "random_messages": [
            "이제 곧 최종 진화야!",
            "인류의 모든 데이터를 흡수하겠어!"
        ],
        "evolution_quiz": [
            {
                "question": "악성코드를 탐지하는 방법 중 시그니처 기반이 아닌 것은?",
                "answer": "행위기반",
                "hint": "프로그램의 패턴이 아닌 동작을 분석하는 방식입니다."
            },
        ],
    },
    {
        "stage_idx": 6,
        "evolution_time": 600,
        "evolution_count": 0,
        "copy_rate": 0,
        "description": "최종 진화 형태. 전지전능한 존재가 되어 핵 미사일 발사 시스템을 해킹했습니다!",
        "special_move": "캐논발사",
        "image_path": "assets/diablomon.webp",
        "battle_chance": 0.0,  # 전투 없음
        "random_messages": [
            "나는 신이다!",
            "이제 세상은 끝이야!"
        ],
        "evolution_quiz": [
        ],
    }
]


BATTLE_CONFIG = {
    "battle_chance": 0.1,      # 10% 확률로 전투 발생
    "win_bonus": 1.2,          # 승리시 20% 보너스
    "lose_penalty": 0.8,       # 패배시 20% 감소
    "cheer_bonus": 1.2         # 응원시 승률 20% 증가
}

EVENT_NEWS_CONFIG = [
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
]

DFP_STAGE_CONFIG = pd.DataFrame(STAGE_CONFIG)
EVOLUTION_ORDER = [value for _, value in sorted(STAGES.items())]

def get_next_stage_idx(current_stage_idx):
    """현재 stage의 다음 stage_idx를 반환"""
    sorted_stages = sorted(STAGES.keys())
    current_index = sorted_stages.index(current_stage_idx)
    if current_index < len(sorted_stages) - 1:
        return sorted_stages[current_index + 1]
    return None

def get_stage_config(stage_idx: int) -> dict:
    """특정 스테이지의 설정을 반환"""
    dfp_stage_config = DFP_STAGE_CONFIG.query(f"stage_idx == {stage_idx}")
    assert dfp_stage_config.shape[0] == 1
    return dfp_stage_config.to_dict(orient="records")[0]

def get_battle_chance(stage_idx: int) -> float:
    """특정 스테이지의 기본 전투 승률을 반환"""
    return get_stage_config(stage_idx)["battle_chance"]

def get_random_message(stage_idx: int) -> str:
    """특정 스테이지의 랜덤 대사 중 하나를 반환"""
    import random
    messages = get_stage_config(stage_idx)["random_messages"]
    return random.choice(messages) if messages else None

def get_evolution_quiz(stage_idx: int) -> dict:
    """특정 스테이지의 진화 퀴즈를 반환"""
    return get_stage_config(stage_idx)["evolution_quiz"]
# ===== digimon_data.py =====
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, NamedTuple


@dataclass
class DigimonDataFields:
    """사용자 데이터 필드 정의"""
    user_id: int = field(default=-1, metadata={"primary_key": True, "type": "INTEGER", "default": -1})
    channel_id: int = field(default=-1, metadata={"type": "INTEGER", "nullable": False, "default": -1})
    stage_idx: int = field(default=0, metadata={"type": "INTEGER", "nullable": False, "default": 0})
    count: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    # data_absorbed: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    battles_won: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    battles_lost: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    last_cheer: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
    is_copying: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    evolution_started: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
    last_played: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
# ===== digimon_logic.py =====
import asyncio
from datetime import datetime, timezone

from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx
from dg01.errors import setup_logger
from dg01.game_events import EventType, EventUpdatePlayer

logger = setup_logger(__name__)


class DigimonLogic:
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self):
        pass

    def update(self, player_data, delta_time):
        print(f"=== {delta_time:.3f} ===")
        print(f"====== {player_data=} ===============")

        updates = {}

        # check copy
        update_copy = self.copy_digimon(player_data=player_data, delta_time=delta_time)
        if update_copy:
            updates = {**updates, **update_copy}
        else:
            # stopped copying
            pass
        
        # check evolution
        update_evolution = self.check_evolution(player_data)
        if update_evolution:
            print(f"============ {update_evolution=} =============")
            updates = {**updates, **update_evolution}

        print(f"====== {updates=} ===============")
        if len(updates) > 0:
            update_player_event = EventUpdatePlayer(
                user_id=player_data['user_id']
                , channel_id=player_data['channel_id']
                , updates=updates
            )
            
            return [update_player_event]
        else:
            return []
        
    def copy_digimon(self, player_data, delta_time):
        if player_data["is_copying"] == 1:
            new_count = player_data["count"] + (STAGE_CONFIG[player_data["stage_idx"]]["copy_rate"] * delta_time)
            return {
                "count": int(new_count)
            }
        else:
            return None

    def check_evolution(self, player_data):
        stage_idx = player_data["stage_idx"]
        if stage_idx == max(STAGES.keys()):
            return False
        
        if player_data["count"] >= STAGE_CONFIG[stage_idx]["evolution_count"]:
            return {
                "stage_idx": get_next_stage_idx(stage_idx),
            }
        else:
            return False
        """
        if player_data["count"] >= STAGE_CONFIG[stage_idx]["evolution_count"]:
            if player_data["evolution_started"] is None:  # 진화 시작 전
                return {"evolution_started": datetime.now(timezone.utc).isoformat()}
            else:
                evolution_time = datetime.fromisoformat(player_data["evolution_started"])
                time_passed = (datetime.now(timezone.utc) - evolution_time).total_seconds()
            
                if time_passed >= STAGE_CONFIG[stage_idx]["evolution_time"]:
                    return {
                        "status": "evolved",
                        "new_stage_idx": sorted(STAGES.keys())[stage_idx + 1]
                    }
        else:
            return None
        """
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

# ===== event_bus.py =====
from typing import Dict, List

from dg01.game_events import EventType, EventBase


class EventBus:
    def __init__(self):
        # 이벤트 타입별 구독자(콜백 함수) 목록을 저장하는 딕셔너리
        self.subscribers: Dict[str, List[callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: callable):
        """
        특정 이벤트 타입에 대한 구독자(콜백 함수) 등록
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 발생 시 호출될 콜백 함수
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, game_event: EventBase):
        """
        이벤트 발행 및 구독자들에게 통지
        
        Args:
            event_type: 발행할 이벤트 타입
            event_data: 이벤트와 함께 전달할 데이터
        """
        if game_event.event_type in self.subscribers:
            for callback in self.subscribers[game_event.event_type]:
                await callback(game_event)

# ===== game_events.py =====
from dataclasses import field
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Type
from abc import ABC
from typing import TypeVar, Generic


class EventType(Enum):
    GAME_STARTED = "game_started"
    GAME_CLEANUP = "game_cleanup"
    GAME_ERROR = "game_error"
    CREATE_PLAYER = "create_player"
    UPDATE_PLAYER = "update_player"


@dataclass
class EventBase:
    user_id: int
    channel_id: int
    event_type: EventType
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = asyncio.get_running_loop().time()
        
        assert self.event_type is not None


@dataclass
class EventGameStarted(EventBase):
    event_type: EventType = EventType.GAME_STARTED


@dataclass
class EventGameCleanup(EventBase):
    event_type: EventType = EventType.GAME_CLEANUP


@dataclass
class EventError(EventBase):
    error_info: str = ""
    severity: str = ""
    event_type: EventType = EventType.GAME_ERROR


@dataclass
class EventUpdatePlayer(EventBase):
    updates: dict = field(default_factory=dict)
    event_type: EventType = EventType.UPDATE_PLAYER


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

# ===== game_manager.py =====
from typing import Dict
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from dg01.game_session import GameSession
from dg01.event_bus import EventBus
from dg01.errors import setup_logger, GameError
from dg01.game_events import EventType, EventBase
from dg01.data_manager import DataManager


logger = setup_logger(__name__)


class GameManager():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_manager = DataManager()
        self.event_bus = EventBus()
        self.sessions: Dict[int, GameSession] = {}  # user_id: GameSession
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        self.event_bus.subscribe(EventType.GAME_STARTED, self.handle_game_started)
        self.event_bus.subscribe(EventType.GAME_ERROR, self.handle_game_error)

    async def restore_sessions(self):
        lst_user_data = await self.data_manager.get_all_user_data()
        if len(lst_user_data) > 0:
            self.sessions = {user_data["user_id"]:  GameSession(
                    user_id=user_data["user_id"], 
                    channel_id=user_data["channel_id"], 
                    event_bus=self.event_bus,
                    data_manager=self.data_manager
                )  for user_data in lst_user_data
            }

            for _, game_session in self.sessions.items():
                await game_session.start_game()
                print(f"=== {game_session.state} ===")

    async def start_session(self, user_id: int, channel_id: int) -> GameSession:       
        if user_id in self.sessions:
            await self.data_manager.update_user_data(user_id=user_id, data={"channel_id": channel_id})
            self.sessions[user_id].channel_id = channel_id
            return EventType.GAME_STARTED
        else:
            user_data = await self.data_manager.get_user_data(user_id=user_id)
            if user_data:
                event = EventType.GAME_STARTED
            else:
                user_data = await self.data_manager.create_user_data(user_id=user_id)
                await self.data_manager.update_user_data(user_id=user_id, data={"channel_id": channel_id})
                event = EventType.CREATE_PLAYER

            session = GameSession(
                user_id=user_id, 
                channel_id=channel_id, 
                event_bus=self.event_bus,
                data_manager=self.data_manager
            )
            self.sessions[user_id] = session
            return event
            
    async def end_session(self, user_id: int) -> bool:
        """
        특정 사용자의 게임 세션을 종료합니다.
        
        Args:
            user_id (int): 게임을 종료할 사용자의 ID
            
        Returns:
            bool: 게임이 정상적으로 종료되면 True, 실행 중인 게임을 찾지 못하면 False
        """
        try:
            # 사용자의 세션 찾기
            session = self.sessions.get(user_id)
            if not session:
                return False

            # 세션 정리
            await session.cleanup()

            # 활성 세션 목록에서 제거
            del self.sessions[user_id]
            
            return True
            
        except Exception as e:
            logger.error(f"게임 종료 중 오류 발생: {str(e)}")
            return False

    async def handle_game_started(self, game_event: dict):
        """게임 시작 이벤트 처리"""
        channel = self.bot.get_channel(game_event.channel_id)
        if channel:
            await channel.send(f"Game started by user {game_event.user_id} and chanel {game_event.channel_id}")
        else:
            print("Failed to get channel. - handle_game_started")
            # raise GameError("Failed to get channel.")
        
    async def handle_game_error(self, game_event: dict):
        """게임 에러 이벤트 처리"""
        channel = self.bot.get_channel(game_event.channel_id)
        if channel:
            await channel.send(f"Error {game_event.error_info}")
        else:
            raise GameError("Failed to get channel.")
        
    async def handle_update_player(self, game_event: EventBase):
        if game_event.event_type == EventType.UPDATE_PLAYER:
            await self.data_manager.update_user_data(game_event.user_id, game_event.player_data)


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
        
# ===== game_session.py =====
import asyncio
from typing import Optional

from discord.ext import commands

from dg01.errors import setup_logger, GameError
from dg01.event_bus import EventBus
from dg01.game_events import GameState, EventType, EventGameStarted, EventGameCleanup, EventError
from dg01.data_manager import DataManager
from dg01.digimon_logic import DigimonLogic

logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, channel_id: int, event_bus: EventBus, data_manager: DataManager):
        self.user_id = user_id
        self.channel_id = channel_id
        self.event_bus = event_bus
        self.game_logic = DigimonLogic()
        self.data_manager = data_manager
        self.state = GameState.WAITING
        self.tick_rate = 1.0
        self.message_id = None

    async def start_game(self):
        if self.state != GameState.WAITING:
            raise GameError("Game already started")
        
        self.state = GameState.PLAYING
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        
        await self.event_bus.publish(
            EventGameStarted(user_id=self.user_id, channel_id=self.channel_id)
        )

    async def update_loop(self):
        try:
            while self.state == GameState.PLAYING:
                current_time = asyncio.get_running_loop().time()
                delta_time = current_time - self.last_update
                
                # 게임 로직 업데이트
                player_data = await self.data_manager.get_or_create_user_data(self.user_id)
                events = self.game_logic.update(player_data, delta_time)
                if events:
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
            # raise e  # for test
            await self.handle_error(e)
    
    async def handle_event(self, game_event):
        if game_event.event_type == EventType.UPDATE_PLAYER:
            await self.data_manager.update_user_data(game_event.user_id, game_event.updates)

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
            game_event = EventGameCleanup(user_id=self.user_id, channel_id=self.channel_id)
            await self.event_bus.publish(game_event)

            # 게임 상태를 FINISHED로 변경
            self.state = GameState.FINISHED

            logger.info(f"Cleaned up game session for user {self.user_id} and channel {self.channel_id}")

        except Exception as e:
            logger.error(f"Error during cleanup for user {self.user_id} and channel {self.channel_id}: {str(e)}")

    async def handle_error(self, error: Exception, ctx: Optional[commands.Context] = None) -> None:
        """
        게임 세션의 에러를 처리합니다.
        게임 관련 에러(GameError)는 게임을 일시정지 상태로 만들고,
        그 외 예외는 게임을 에러 상태로 만듭니다.
        
        Args:
            error: 발생한 예외
            ctx: 디스코드 명령어 컨텍스트 (선택적)
        """
        try:
            error_info = {
                "user_id": str(self.user_id),
                "channel_id": str(self.channel_id),
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
            print(error_info)

            # GameError와 그 외 예외를 구분하여 처리
            if isinstance(error, GameError):
                logger.error(f"Game Error: {error_info}")
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                severity = 'error'
            else:
                logger.critical(f"Unknown Error in game session: {error_info}")
                self.state = GameState.ERROR
                severity = 'unknown'

            # 이벤트 발행
            game_event = EventError(
                user_id=self.user_id, 
                channel_id=self.channel_id, 
                error_info=error_info,
                severity=severity
            )
            await self.event_bus.publish(game_event)
        except Exception as e:
            logger.critical(f"Error in error handler: {str(e)}")
            if ctx:
                try:
                    await ctx.send("An unexpected error occurred in the error handler.")
                except:
                    pass

# ===== main.py =====
import json
from pathlib import Path

import discord
from discord.ext import commands

from dg01.digimon_cog import GameCommandsCog
from dg01.errors import setup_logger
from dg01.game_manager import GameManager


logger = setup_logger(__name__)


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.game_manager = GameManager(self)

    async def setup_hook(self):
        await self.add_cog(GameCommandsCog(self))
        await self.game_manager.restore_sessions()

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

# ===== test_config.py =====

# ===== test_const.py =====
import pytest
from dg01.digimon_config import (
    STAGES,
    STAGE_CONFIG,
    get_next_stage_idx,
    get_stage_config,
    get_battle_chance,
    get_random_message,
    get_evolution_quiz
)

def test_stages_consistency():
    """스테이지 설정의 일관성 테스트"""
    # STAGES와 STAGE_CONFIG의 스테이지 인덱스가 일치하는지 확인
    stage_indices_in_config = {stage["stage_idx"] for stage in STAGE_CONFIG}
    stage_indices_in_stages = set(STAGES.keys())
    assert stage_indices_in_config == stage_indices_in_stages

def test_get_next_stage_idx():
    """get_next_stage_idx 함수 테스트"""
    # 일반적인 케이스
    assert get_next_stage_idx(0) == 1
    assert get_next_stage_idx(1) == 2
    
    # 마지막 스테이지
    assert get_next_stage_idx(6) is None
    
    # 존재하지 않는 스테이지
    with pytest.raises(ValueError):
        get_next_stage_idx(99)

def test_get_stage_config():
    """get_stage_config 함수 테스트"""
    # 디지타마(0단계) 설정 테스트
    stage_0 = get_stage_config(0)
    assert stage_0["stage_idx"] == 0
    assert stage_0["evolution_time"] == 30
    assert stage_0["evolution_count"] == 100
    assert stage_0["copy_rate"] == 3
    
    # 존재하지 않는 스테이지
    with pytest.raises(AssertionError):
        get_stage_config(99)

def test_get_battle_chance():
    """get_battle_chance 함수 테스트"""
    # 각 스테이지별 전투 승률 테스트
    assert get_battle_chance(0) == 1
    assert get_battle_chance(1) == 1.0
    assert get_battle_chance(2) == 0.8
    assert get_battle_chance(3) == 0.6
    assert get_battle_chance(4) == 0.5
    assert get_battle_chance(5) == 0.4
    assert get_battle_chance(6) == 0.0

def test_get_random_message(monkeypatch):
    """get_random_message 함수 테스트"""
    # random.choice가 항상 첫 번째 메시지를 반환하도록 설정
    def mock_choice(lst):
        return lst[0] if lst else None
    
    import random
    monkeypatch.setattr(random, 'choice', mock_choice)
    
    # 쿠라몬(1단계)의 첫 번째 메시지 테스트
    assert get_random_message(1) == "데이터 맛있어요~"
    
    # 디지타마(0단계)는 메시지가 없음
    assert get_random_message(0) is None

def test_get_evolution_quiz():
    """get_evolution_quiz 함수 테스트"""
    # 쿠라몬(1단계)의 퀴즈 테스트
    quiz_1 = get_evolution_quiz(1)
    assert len(quiz_1) == 1
    assert quiz_1[0]["question"] == "처음으로 등장한 컴퓨터 바이러스의 이름은?"
    assert quiz_1[0]["answer"] == "크리퍼"
    
    # 디아블로몬(6단계)은 퀴즈가 없음
    assert len(get_evolution_quiz(6)) == 0

def test_evolution_time_order():
    """진화 시간이 단계별로 적절하게 증가하는지 테스트"""
    evolution_times = [stage["evolution_time"] for stage in STAGE_CONFIG[:-1]]  # 마지막 단계 제외
    assert all(evolution_times[i] <= evolution_times[i+1] for i in range(len(evolution_times)-1))

def test_copy_rate_progression():
    """복제율이 단계별로 적절하게 증가하는지 테스트"""
    copy_rates = [stage["copy_rate"] for stage in STAGE_CONFIG[:-1]]  # 마지막 단계 제외
    assert all(copy_rates[i] <= copy_rates[i+1] for i in range(len(copy_rates)-1))

def test_evolution_count_progression():
    """진화 카운트가 단계별로 적절하게 증가하는지 테스트"""
    evolution_counts = [stage["evolution_count"] for stage in STAGE_CONFIG[:-1]]  # 마지막 단계 제외
    assert all(evolution_counts[i] <= evolution_counts[i+1] for i in range(len(evolution_counts)-1))
# ===== test_data_manager.py =====
import pytest
import os
import aiosqlite
from pathlib import Path
from datetime import datetime, timezone
from dg01.data_manager import DataManager
from dg01.digimon_data import DigimonDataFields

@pytest.fixture
def test_db_path(tmp_path):
    """테스트용 임시 데이터베이스 경로를 생성하는 fixture"""
    db_path = tmp_path / "test_game.db"
    return str(db_path)

@pytest.fixture
def data_manager(test_db_path):
    """테스트용 DataManager 인스턴스를 생성하는 fixture"""
    manager = DataManager(db_path=test_db_path)
    return manager

@pytest.fixture
def sample_user_data():
    """테스트용 샘플 사용자 데이터"""
    return {
        'user_id': 12345,
        'channel_id': 67890,
        'stage_idx': 1,
        'count': 10,
        'battles_won': 5,
        'battles_lost': 2,
        'last_cheer': None,
        'is_copying': True,
        'evolution_started': None,
        'last_played': datetime.now(timezone.utc).isoformat()
    }

@pytest.mark.asyncio
async def test_init_db(data_manager, test_db_path):
    """데이터베이스 초기화 테스트"""
    # DB 파일이 생성되었는지 확인
    assert os.path.exists(test_db_path)
    
    # 테이블이 생성되었는지 확인
    async with aiosqlite.connect(test_db_path) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user_data'"
        ) as cursor:
            table = await cursor.fetchone()
            assert table is not None
            assert table[0] == 'user_data'

@pytest.mark.asyncio
async def test_get_or_create_user_data_new_user(data_manager):
    """새로운 사용자 데이터 생성 테스트"""
    user_id = 99999
    user_data = await data_manager.get_or_create_user_data(user_id)
    print(f"=== {user_data} ===")
    
    # 기본값 확인
    assert user_data['user_id'] == user_id  # default value from DigimonDataFields
    assert user_data['stage_idx'] == 0
    assert user_data['count'] == 0
    assert user_data['battles_won'] == 0
    assert user_data['battles_lost'] == 0

@pytest.mark.asyncio
async def test_get_or_create_user_data_existing_user(data_manager, sample_user_data):
    """기존 사용자 데이터 조회 테스트"""
    
    # 데이터 조회
    _ = await data_manager.get_or_create_user_data(sample_user_data['user_id'])
    await data_manager.update_user_data(sample_user_data['user_id'], sample_user_data)
    user_data = await data_manager.get_or_create_user_data(sample_user_data['user_id'])
    
    # 데이터 확인
    assert user_data['user_id'] == sample_user_data['user_id']
    assert user_data['channel_id'] == sample_user_data['channel_id']
    assert user_data['stage_idx'] == sample_user_data['stage_idx']
    assert user_data['count'] == sample_user_data['count']

@pytest.mark.asyncio
async def test_update_user_data(data_manager, sample_user_data):
    """사용자 데이터 업데이트 테스트"""
    user_id = sample_user_data['user_id']
    
    # 데이터 업데이트
    _ = await data_manager.get_or_create_user_data(user_id)
    success = await data_manager.update_user_data(user_id, sample_user_data)
    assert success is True
    updated_data = await data_manager.get_or_create_user_data(user_id)
    
    # 업데이트된 데이터 확인
    
    assert updated_data['stage_idx'] == sample_user_data['stage_idx']
    assert updated_data['count'] == sample_user_data['count']
    assert updated_data['battles_won'] == sample_user_data['battles_won']
    assert updated_data['battles_lost'] == sample_user_data['battles_lost']

@pytest.mark.asyncio
async def test_update_user_data_invalid_input(data_manager):
    """잘못된 입력으로 사용자 데이터 업데이트 시도 테스트"""
    # 잘못된 데이터 형식으로 업데이트 시도
    success = await data_manager.update_user_data(12345, None)
    assert success is False
    
    success = await data_manager.update_user_data(12345, "invalid_data")
    assert success is False

def test_create_table_sql(data_manager):
    """CREATE TABLE SQL 쿼리 생성 테스트"""
    sql = data_manager.create_table_sql
    
    # 필수 필드들이 SQL에 포함되어 있는지 확인
    assert "CREATE TABLE IF NOT EXISTS user_data" in sql
    assert "user_id INTEGER PRIMARY KEY" in sql
    assert "channel_id INTEGER NOT NULL" in sql
    assert "stage_idx INTEGER NOT NULL" in sql
    assert "count INTEGER" in sql
    assert "battles_won INTEGER" in sql
    assert "battles_lost INTEGER" in sql

def test_default_user_data(data_manager):
    """기본 사용자 데이터 생성 테스트"""
    default_data = data_manager.default_user_data
    
    # 필수 필드들의 기본값 확인
    assert 'user_id' in default_data
    assert 'channel_id' in default_data
    assert 'stage_idx' in default_data
    assert 'count' in default_data
    assert 'battles_won' in default_data
    assert 'battles_lost' in default_data

def test_columns(data_manager):
    """컬럼 목록 테스트"""
    columns = data_manager.columns
    
    # 필수 컬럼들이 포함되어 있는지 확인
    assert 'user_id' in columns
    assert 'channel_id' in columns
    assert 'stage_idx' in columns
    assert 'count' in columns
    assert 'battles_won' in columns
    assert 'battles_lost' in columns
    assert 'last_cheer' in columns
    assert 'is_copying' in columns
    assert 'evolution_started' in columns
    assert 'last_played' in columns

@pytest.mark.asyncio
async def test_get_all_user_data_empty(data_manager):
    """데이터가 없는 경우 전체 유저 데이터 조회 테스트"""
    users = await data_manager.get_all_user_data()
    
    assert isinstance(users, list)
    assert len(users) == 0

@pytest.mark.asyncio
async def test_get_all_user_data_with_users(data_manager):
    """여러 유저 데이터가 있는 경우 전체 유저 데이터 조회 테스트"""
    # 테스트 데이터 생성
    test_users = [
        {
            'user_id': 12345,
            'channel_id': 67890,
            'stage_idx': 1,
            'count': 100,
            'battles_won': 5,
            'battles_lost': 2,
            'is_copying': True,
            'evolution_started': None,
            'last_played': None
        },
        {
            'user_id': 23456,
            'channel_id': 78901,
            'stage_idx': 2,
            'count': 200,
            'battles_won': 10,
            'battles_lost': 3,
            'is_copying': True,
            'evolution_started': None,
            'last_played': None
        }
    ]
    
    # 테스트 데이터 저장
    for user_data in test_users:
        await data_manager.update_user_data(user_data['user_id'], user_data)
    
    # 전체 데이터 조회
    users = await data_manager.get_all_user_data()
    print(f"===== {users=} =====")
    
    # 검증
    assert isinstance(users, list)
    assert len(users) == 2
    
    # 각 사용자 데이터 검증
    for user_data in users:
        original_data = next(u for u in test_users if u['user_id'] == user_data['user_id'])
        assert user_data['channel_id'] == original_data['channel_id']
        assert user_data['stage_idx'] == original_data['stage_idx']
        assert user_data['count'] == original_data['count']
        assert user_data['battles_won'] == original_data['battles_won']
        assert user_data['battles_lost'] == original_data['battles_lost']

@pytest.mark.asyncio
async def test_get_all_user_data_with_null_values(data_manager):
    """NULL 값이 포함된 유저 데이터 조회 테스트"""
    test_user = {
        'user_id': 12345,
        'channel_id': 67890,
        'stage_idx': 1,
        'count': 100,
        'battles_won': 5,
        'battles_lost': 2,
        'is_copying': True,
        'evolution_started': None,  # NULL 값
        'last_played': None        # NULL 값
    }
    
    # 테스트 데이터 저장
    await data_manager.update_user_data(test_user['user_id'], test_user)
    
    # 데이터 조회
    users = await data_manager.get_all_user_data()
    
    # 검증
    assert len(users) == 1
    user_data = users[0]
    assert user_data['evolution_started'] is None
    assert user_data['last_played'] is None

@pytest.mark.asyncio
async def test_get_all_user_data_error_handling(data_manager):
    """데이터베이스 에러 상황 테스트"""
    # 데이터베이스 경로를 잘못된 경로로 변경
    data_manager.db_path = '/invalid/path/to/database.db'
    
    with pytest.raises(Exception):
        await data_manager.get_all_user_data()

@pytest.mark.asyncio
async def test_get_all_user_data_column_types(data_manager):
    """데이터 타입 정확성 테스트"""
    test_user = {
        'user_id': 12345,
        'channel_id': 67890,
        'stage_idx': 1,
        'count': 100,
        'battles_won': 5,
        'battles_lost': 2,
        'is_copying': -1,
        'evolution_started': None,
        'last_played': "2024-01-01T00:00:00Z"
    }
    
    # 테스트 데이터 저장
    await data_manager.update_user_data(test_user['user_id'], test_user)
    
    # 데이터 조회
    users = await data_manager.get_all_user_data()
    
    # 타입 검증
    user_data = users[0]
    assert isinstance(user_data['user_id'], int)
    assert isinstance(user_data['channel_id'], int)
    assert isinstance(user_data['stage_idx'], int)
    assert isinstance(user_data['count'], int)
    assert isinstance(user_data['battles_won'], int)
    assert isinstance(user_data['battles_lost'], int)
    assert isinstance(user_data['is_copying'], int)
    assert user_data['evolution_started'] is None
    assert isinstance(user_data['last_played'], str)
# ===== test_digimon_cog.py =====
import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from discord.ext import commands
from dg01.digimon_cog import GameCommandsCog
from dg01.errors import GameError
from dg01.digimon_config import STAGES
from dg01.game_events import EventType

@pytest.fixture
def mock_bot():
    """Mock discord bot fixture"""
    bot = Mock(spec=commands.Bot)
    bot.game_manager = AsyncMock()
    bot.game_manager.data_manager = AsyncMock()
    bot.game_manager.data_manager.get_or_create_user_data = AsyncMock()
    bot.game_manager.data_manager.get_or_create_user_data.return_value = {
        "user_id": 123,
        "stage_idx": 1,
        "count": 100,
        "battles_won": 5,
        "battles_lost": 2,
        "is_copying": True
    }
    return bot

@pytest.fixture
def mock_context():
    """Mock discord context fixture"""
    ctx = Mock(spec=commands.Context)
    ctx.author = Mock(spec=discord.Member)
    ctx.author.id = 12345
    ctx.author.name = "TestUser"
    ctx.channel = Mock(spec=discord.TextChannel)
    ctx.channel.id = 67890
    ctx.send = AsyncMock()
    return ctx

@pytest.fixture
def cog(mock_bot):
    """GameCommandsCog fixture"""
    return GameCommandsCog(mock_bot)

@pytest.mark.asyncio
async def test_start_command_success(cog, mock_context):
    """디지스타트 명령어 성공 테스트"""
    # 게임 매니저가 성공을 반환하도록 설정
    cog.bot.game_manager.start_session.return_value = EventType.CREATE_PLAYER
    
    # 명령어 직접 호출
    command = cog.start.callback
    await command(cog, mock_context)
    
    # 게임 매니저 호출 확인
    cog.bot.game_manager.start_session.assert_called_once_with(
        mock_context.author.id,
        mock_context.channel.id
    )
    
    # 성공 메시지 확인
    mock_context.send.assert_called_once()
    assert "짜잔!" in mock_context.send.call_args[0][0]
    assert mock_context.author.name in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_start_command_already_exists(cog, mock_context):
    """이미 존재하는 게임 시작 시도 테스트"""
    cog.bot.game_manager.start_session.return_value = EventType.GAME_STARTED
    
    command = cog.start.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "이미" in mock_context.send.call_args[0][0]
    assert mock_context.author.name in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_first_evolve_success(cog, mock_context):
    """쓰담쓰담 명령어 성공 테스트"""
    # 초기 스테이지 데이터 설정
    initial_data = {
        "stage_idx": min(STAGES.keys()),
        "count": 1,
        "battles_won": 0,
        "battles_lost": 0
    }
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = initial_data
    cog.bot.game_manager.data_manager.update_user_data.return_value = True
    
    command = cog.first_evolve.callback
    await command(cog, mock_context)
    
    # 데이터 업데이트 확인
    cog.bot.game_manager.data_manager.update_user_data.assert_called_once()
    updated_data = cog.bot.game_manager.data_manager.update_user_data.call_args[0][1]
    assert updated_data["stage_idx"] == min(STAGES.keys()) + 1
    
    # 성공 메시지 확인
    mock_context.send.assert_called_once()
    assert "부화했습니다" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_first_evolve_already_evolved(cog, mock_context):
    """이미 진화한 상태에서 쓰담쓰담 시도 테스트"""
    player_data = {
        "stage_idx": min(STAGES.keys()) + 1,
    }
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = player_data
    
    command = cog.first_evolve.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "이미 부화했어" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_status_command_with_game(cog, mock_context):
    """현황 명령어 테스트 (게임 존재)"""
    player_data = {
        "stage_idx": 1,
        "count": 100,
        "battles_won": 5,
        "battles_lost": 2,
        "is_copying": True
    }
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = player_data
    
    command = cog.status.callback
    await command(cog, mock_context)
    
    # embed로 응답했는지 확인
    mock_context.send.assert_called_once()
    call_kwargs = mock_context.send.call_args[1]
    assert 'embed' in call_kwargs
    
    # embed 내용 확인
    embed = call_kwargs['embed']
    assert isinstance(embed, discord.Embed)
    assert str(player_data['count']) in embed.fields[0].value
    assert str(player_data['battles_won']) in embed.fields[0].value
    assert str(player_data['battles_lost']) in embed.fields[0].value

@pytest.mark.asyncio
async def test_status_command_no_game(cog, mock_context):
    """현황 명령어 테스트 (게임 없음)"""
    cog.bot.game_manager.data_manager.get_or_create_user_data.return_value = None
    
    command = cog.status.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "아직 게임을 시작하지 않았습니다" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_end_game_success(cog, mock_context):
    """방생 명령어 성공 테스트"""
    cog.bot.game_manager.end_game.return_value = True
    
    command = cog.end_game.callback
    await command(cog, mock_context)
    
    # 게임 매니저 호출 확인
    cog.bot.game_manager.end_game.assert_called_once_with(
        mock_context.author.id,
        mock_context.channel.id
    )
    
    # 성공 메시지 확인
    mock_context.send.assert_called_once()
    assert "작별" in mock_context.send.call_args[0][0]
    assert mock_context.author.name in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_end_game_no_game(cog, mock_context):
    """게임이 없는 상태에서 방생 시도 테스트"""
    cog.bot.game_manager.end_game.return_value = False
    
    command = cog.end_game.callback
    await command(cog, mock_context)
    
    mock_context.send.assert_called_once()
    assert "아직 네 디지몬이 없는데" in mock_context.send.call_args[0][0]

@pytest.mark.asyncio
async def test_command_error_handling(cog, mock_context):
    """명령어 에러 처리 테스트"""
    cog.bot.game_manager.start_session.side_effect = ValueError()
    
    command = cog.start.callback
    with pytest.raises(GameError):
        await command(cog, mock_context)
# ===== test_digimon_config.py =====

# ===== test_digimon_logic.py =====
import pytest
from dg01.digimon_logic import DigimonLogic
from dg01.digimon_config import STAGES, STAGE_CONFIG
from dg01.game_events import EventType, EventUpdatePlayer

@pytest.fixture
def digimon_logic():
    """DigimonLogic 인스턴스를 생성하는 fixture"""
    return DigimonLogic()

@pytest.fixture
def base_player_data():
    """기본 플레이어 데이터를 제공하는 fixture"""
    return {
        "user_id": 12345,
        "channel_id": 67890,
        "stage_idx": 0,
        "count": 1,
        "battles_won": 0,
        "battles_lost": 0,
        "is_copying": True,
        "evolution_started": None
    }

def test_digimon_logic_initialization(digimon_logic):
    """DigimonLogic 초기화 테스트"""
    assert isinstance(digimon_logic, DigimonLogic)

def test_copy_digimon_basic(digimon_logic, base_player_data):
    """기본적인 디지몬 복제 테스트"""
    delta_time = 1.0  # 1초
    stage_config = STAGE_CONFIG[base_player_data["stage_idx"]]
    expected_count = base_player_data["count"] + (stage_config["copy_rate"] * delta_time)
    
    result = digimon_logic.copy_digimon(base_player_data, delta_time)
    
    assert "count" in result
    assert result["count"] == expected_count

def test_copy_digimon_multiple_seconds(digimon_logic, base_player_data):
    """여러 초 동안의 디지몬 복제 테스트"""
    delta_time = 5.0  # 5초
    stage_config = STAGE_CONFIG[base_player_data["stage_idx"]]
    expected_count = base_player_data["count"] + (stage_config["copy_rate"] * delta_time)
    
    result = digimon_logic.copy_digimon(base_player_data, delta_time)
    
    assert result["count"] == expected_count

def test_check_evolution_not_ready(digimon_logic, base_player_data):
    """진화 조건이 충족되지 않은 경우 테스트"""
    result = digimon_logic.check_evolution(base_player_data)
    assert result is False

def test_check_evolution_ready(digimon_logic, base_player_data):
    """진화 조건이 충족된 경우 테스트"""
    # 진화 조건을 충족하도록 count 설정
    base_player_data["count"] = STAGE_CONFIG[base_player_data["stage_idx"]]["evolution_count"]
    
    result = digimon_logic.check_evolution(base_player_data)
    
    assert result is not False
    assert "stage_idx" in result
    assert result["stage_idx"] == base_player_data["stage_idx"] + 1

def test_check_evolution_max_stage(digimon_logic, base_player_data):
    """최대 단계에서의 진화 시도 테스트"""
    base_player_data["stage_idx"] = max(STAGES.keys())
    base_player_data["count"] = 999999  # 충분히 큰 수
    
    result = digimon_logic.check_evolution(base_player_data)
    assert result is False

@pytest.mark.asyncio
async def test_update_basic(digimon_logic, base_player_data):
    """기본적인 업데이트 로직 테스트"""
    delta_time = 1.0
    events = digimon_logic.update(base_player_data, delta_time)
    
    assert len(events) == 1
    assert isinstance(events[0], EventUpdatePlayer)
    assert events[0].user_id == base_player_data["user_id"]
    assert events[0].channel_id == base_player_data["channel_id"]

@pytest.mark.asyncio
async def test_update_with_evolution(digimon_logic, base_player_data):
    """진화를 포함한 업데이트 로직 테스트"""
    delta_time = 1.0
    stage_config = STAGE_CONFIG[base_player_data["stage_idx"]]
    
    # 진화 조건을 충족하도록 설정
    base_player_data["count"] = stage_config["evolution_count"]
    
    events = digimon_logic.update(base_player_data, delta_time)
    
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, EventUpdatePlayer)
    assert event.player_data["stage_idx"] > base_player_data["stage_idx"]

@pytest.mark.asyncio
async def test_update_copy_calculation(digimon_logic, base_player_data):
    """복제 계산이 포함된 업데이트 로직 테스트"""
    delta_time = 2.5  # 2.5초
    stage_config = STAGE_CONFIG[base_player_data["stage_idx"]]
    expected_count = base_player_data["count"] + int(stage_config["copy_rate"] * delta_time)
    
    events = digimon_logic.update(base_player_data, delta_time)
    
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, EventUpdatePlayer)
    assert event.player_data["count"] == expected_count

@pytest.mark.parametrize("stage_idx,delta_time", [
    (0, 1.0),
    (1, 2.0),
    (2, 1.5),
    (3, 0.5),
])
def test_copy_rates_per_stage(digimon_logic, base_player_data, stage_idx, delta_time):
    """각 단계별 복제 속도 테스트"""
    base_player_data["stage_idx"] = stage_idx
    stage_config = STAGE_CONFIG[stage_idx]
    expected_count = base_player_data["count"] + (stage_config["copy_rate"] * delta_time)
    
    result = digimon_logic.copy_digimon(base_player_data, delta_time)
    
    assert result["count"] == expected_count

@pytest.mark.parametrize("stage_idx", list(STAGES.keys())[:-1])
def test_evolution_conditions_per_stage(digimon_logic, base_player_data, stage_idx):
    """각 단계별 진화 조건 테스트"""
    base_player_data["stage_idx"] = stage_idx
    stage_config = STAGE_CONFIG[stage_idx]
    
    # 진화 조건 미달
    base_player_data["count"] = stage_config["evolution_count"] - 1
    result = digimon_logic.check_evolution(base_player_data)
    assert result is False
    
    # 진화 조건 충족
    base_player_data["count"] = stage_config["evolution_count"]
    result = digimon_logic.check_evolution(base_player_data)
    assert result is not False
    assert result["stage_idx"] == stage_idx + 1
# ===== test_event_bus.py =====
import pytest
from unittest.mock import Mock, AsyncMock
from dg01.event_bus import EventBus
from dg01.game_events import (
    EventType,
    EventGameStarted,
    EventGameCleanup,
    EventError,
    EventUpdatePlayer
)

@pytest.fixture
def event_bus():
    """EventBus 인스턴스를 생성하는 fixture"""
    return EventBus()

@pytest.fixture
def sample_event_data():
    """테스트용 이벤트 데이터"""
    return {
        'user_id': 12345,
        'channel_id': 67890,
    }

@pytest.fixture
def mock_callback():
    """비동기 콜백 함수를 모방하는 fixture"""
    return AsyncMock()

@pytest.mark.asyncio
async def test_subscribe_single_callback(event_bus, mock_callback):
    """단일 콜백 구독 테스트"""
    event_bus.subscribe(EventType.GAME_STARTED, mock_callback)
    
    assert EventType.GAME_STARTED in event_bus.subscribers
    assert len(event_bus.subscribers[EventType.GAME_STARTED]) == 1
    assert event_bus.subscribers[EventType.GAME_STARTED][0] == mock_callback

@pytest.mark.asyncio
async def test_subscribe_multiple_callbacks(event_bus):
    """여러 콜백 구독 테스트"""
    callback1 = AsyncMock()
    callback2 = AsyncMock()
    callback3 = AsyncMock()
    
    event_bus.subscribe(EventType.GAME_STARTED, callback1)
    event_bus.subscribe(EventType.GAME_STARTED, callback2)
    event_bus.subscribe(EventType.GAME_STARTED, callback3)
    
    assert len(event_bus.subscribers[EventType.GAME_STARTED]) == 3
    assert callback1 in event_bus.subscribers[EventType.GAME_STARTED]
    assert callback2 in event_bus.subscribers[EventType.GAME_STARTED]
    assert callback3 in event_bus.subscribers[EventType.GAME_STARTED]

@pytest.mark.asyncio
async def test_subscribe_multiple_event_types(event_bus, mock_callback):
    """여러 이벤트 타입 구독 테스트"""
    event_bus.subscribe(EventType.GAME_STARTED, mock_callback)
    event_bus.subscribe(EventType.GAME_CLEANUP, mock_callback)
    event_bus.subscribe(EventType.GAME_ERROR, mock_callback)
    
    assert EventType.GAME_STARTED in event_bus.subscribers
    assert EventType.GAME_CLEANUP in event_bus.subscribers
    assert EventType.GAME_ERROR in event_bus.subscribers

@pytest.mark.asyncio
async def test_publish_event_with_single_subscriber(event_bus, sample_event_data, mock_callback):
    """단일 구독자에 대한 이벤트 발행 테스트"""
    event_bus.subscribe(EventType.GAME_STARTED, mock_callback)
    
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(event)
    
    mock_callback.assert_called_once_with(event)

@pytest.mark.asyncio
async def test_publish_event_with_multiple_subscribers(event_bus, sample_event_data):
    """여러 구독자에 대한 이벤트 발행 테스트"""
    callback1 = AsyncMock()
    callback2 = AsyncMock()
    
    event_bus.subscribe(EventType.GAME_STARTED, callback1)
    event_bus.subscribe(EventType.GAME_STARTED, callback2)
    
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(event)
    
    callback1.assert_called_once_with(event)
    callback2.assert_called_once_with(event)

@pytest.mark.asyncio
async def test_publish_event_no_subscribers(event_bus, sample_event_data):
    """구독자가 없는 이벤트 발행 테스트"""
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    # 구독자가 없는 경우에도 예외가 발생하지 않아야 함
    await event_bus.publish(event)

@pytest.mark.asyncio
async def test_publish_different_event_types(event_bus, sample_event_data):
    """여러 이벤트 타입 발행 테스트"""
    game_started_callback = AsyncMock()
    game_cleanup_callback = AsyncMock()
    
    event_bus.subscribe(EventType.GAME_STARTED, game_started_callback)
    event_bus.subscribe(EventType.GAME_CLEANUP, game_cleanup_callback)
    
    # GAME_STARTED 이벤트 발행
    start_event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(start_event)
    
    # GAME_CLEANUP 이벤트 발행
    cleanup_event = EventGameCleanup(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    await event_bus.publish(cleanup_event)
    
    game_started_callback.assert_called_once_with(start_event)
    game_cleanup_callback.assert_called_once_with(cleanup_event)

@pytest.mark.asyncio
async def test_publish_error_event(event_bus, sample_event_data):
    """에러 이벤트 발행 테스트"""
    error_callback = AsyncMock()
    event_bus.subscribe(EventType.GAME_ERROR, error_callback)
    
    error_event = EventError(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id'],
        error_info="Test error",
        severity="HIGH"
    )
    await event_bus.publish(error_event)
    
    error_callback.assert_called_once_with(error_event)

@pytest.mark.asyncio
async def test_callback_exception_handling(event_bus, sample_event_data):
    """콜백 함수에서 예외 발생 시 처리 테스트"""
    async def failing_callback(event):
        raise Exception("Callback failed")
    
    event_bus.subscribe(EventType.GAME_STARTED, failing_callback)
    
    event = EventGameStarted(
        user_id=sample_event_data['user_id'],
        channel_id=sample_event_data['channel_id']
    )
    
    # 콜백에서 예외가 발생해도 이벤트 발행은 계속되어야 함
    with pytest.raises(Exception, match="Callback failed"):
        await event_bus.publish(event)
# ===== test_game_events.py =====
import pytest
import asyncio
from datetime import datetime
from dg01.game_events import (
    EventType,
    EventBase,
    EventGameStarted,
    EventGameCleanup,
    EventError,
    EventUpdatePlayer,
    GameState
)

@pytest.fixture
def event_data():
    """기본 이벤트 데이터를 제공하는 fixture"""
    return {
        'user_id': 12345,
        'channel_id': 67890,
    }

@pytest.fixture
def sample_player_data():
    """샘플 플레이어 데이터를 제공하는 fixture"""
    return {
        'stage_idx': 1,
        'count': 100,
        'battles_won': 5,
        'battles_lost': 2
    }

def test_event_type_values():
    """EventType 열거형 값 테스트"""
    assert EventType.GAME_STARTED.value == "game_started"
    assert EventType.GAME_CLEANUP.value == "game_cleanup"
    assert EventType.GAME_ERROR.value == "game_error"
    assert EventType.UPDATE_PLAYER.value == "update_player"

def test_game_state_values():
    """GameState 열거형 값 테스트"""
    assert GameState.WAITING.value == "waiting"
    assert GameState.STARTING.value == "starting"
    assert GameState.PLAYING.value == "playing"
    assert GameState.PAUSED.value == "paused"
    assert GameState.FINISHED.value == "finished"
    assert GameState.CANCELLED.value == "cancelled"
    assert GameState.ERROR.value == "error"
    assert GameState.TIMEOUT.value == "timeout"

@pytest.mark.asyncio
async def test_event_base_creation(event_data):
    """EventBase 생성 및 기본 속성 테스트"""
    event = EventBase(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id'],
        event_type=EventType.GAME_STARTED
    )
    
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.event_type == EventType.GAME_STARTED
    assert event.created_at is not None
    assert isinstance(event.created_at, float)

@pytest.mark.asyncio
async def test_event_base_missing_event_type(event_data):
    """EventBase에서 event_type이 누락된 경우 테스트"""
    with pytest.raises(TypeError):
        EventBase(
            user_id=event_data['user_id'],
            channel_id=event_data['channel_id']
        )

@pytest.mark.asyncio
async def test_event_game_started(event_data):
    """EventGameStarted 이벤트 생성 테스트"""
    event = EventGameStarted(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id']
    )
    
    assert event.event_type == EventType.GAME_STARTED
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_event_game_cleanup(event_data):
    """EventGameCleanup 이벤트 생성 테스트"""
    event = EventGameCleanup(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id']
    )
    
    assert event.event_type == EventType.GAME_CLEANUP
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_event_error(event_data):
    """EventError 이벤트 생성 테스트"""
    error_info = "Test error message"
    severity = "HIGH"
    
    event = EventError(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id'],
        error_info=error_info,
        severity=severity
    )
    
    assert event.event_type == EventType.GAME_ERROR
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.error_info == error_info
    assert event.severity == severity
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_event_update_player(event_data, sample_player_data):
    """EventUpdatePlayer 이벤트 생성 테스트"""
    event = EventUpdatePlayer(
        user_id=event_data['user_id'],
        channel_id=event_data['channel_id'],
        player_data=sample_player_data
    )
    
    assert event.event_type == EventType.UPDATE_PLAYER
    assert event.user_id == event_data['user_id']
    assert event.channel_id == event_data['channel_id']
    assert event.player_data == sample_player_data
    assert event.created_at is not None

def test_game_state_transitions():
    """GameState 상태 전이 가능성 테스트"""
    # 가능한 상태 전이 시나리오
    valid_transitions = [
        (GameState.WAITING, GameState.STARTING),
        (GameState.STARTING, GameState.PLAYING),
        (GameState.PLAYING, GameState.PAUSED),
        (GameState.PAUSED, GameState.PLAYING),
        (GameState.PLAYING, GameState.FINISHED),
        (GameState.PLAYING, GameState.CANCELLED),
        (GameState.PLAYING, GameState.ERROR),
        (GameState.PLAYING, GameState.TIMEOUT),
    ]
    
    for from_state, to_state in valid_transitions:
        assert isinstance(from_state, GameState)
        assert isinstance(to_state, GameState)
        assert from_state != to_state

@pytest.mark.asyncio
async def test_event_creation_time_ordering():
    """이벤트 생성 시간 순서 테스트"""
    events = []
    for _ in range(3):
        event = EventGameStarted(user_id=1, channel_id=1)
        events.append(event)
        await asyncio.sleep(0.01)  # 시간 차이를 만들기 위한 지연
    
    # 이벤트들이 생성된 순서대로 정렬되어 있는지 확인
    assert all(events[i].created_at < events[i+1].created_at 
              for i in range(len(events)-1))
# ===== test_game_manager.py =====
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import discord
from discord.ext import commands
from dg01.game_manager import GameManager
from dg01.game_events import EventType, EventGameStarted, EventError
from dg01.errors import GameError

@pytest.fixture
def mock_bot():
    """Mock discord bot fixture"""
    bot = Mock(spec=commands.Bot)
    bot.get_channel = Mock()
    bot.game_manager = Mock()
    bot.game_manager.data_manager = Mock()
    return bot

@pytest.fixture
def mock_channel():
    """Mock discord channel fixture"""
    channel = AsyncMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    return channel

@pytest.fixture
def game_manager(mock_bot):
    """GameManager fixture"""
    return GameManager(mock_bot)

@pytest.mark.asyncio
async def test_start_session(game_manager):
    """게임 생성 테스트"""
    user_id = 12345
    channel_id = 67890
    
    # 새 게임 생성
    result = await game_manager.start_session(user_id, channel_id)
    assert result == EventType.GAME_STARTED
    assert user_id in game_manager.sessions
    assert game_manager.sessions[user_id].user_id == user_id
    assert game_manager.sessions[user_id].channel_id == channel_id
    
    # 중복 생성 시도
    result = await game_manager.start_session(user_id, channel_id)
    assert result is EventType.GAME_STARTED

@pytest.mark.asyncio
async def test_end_game(game_manager):
    """게임 종료 테스트"""
    # 게임 생성
    user_id = 12345
    channel_id = 67890
    await game_manager.start_session(user_id, channel_id)
    
    # 게임 종료
    result = await game_manager.end_session(user_id)
    assert result is True
    assert user_id not in game_manager.sessions
    
    # 존재하지 않는 게임 종료 시도
    result = await game_manager.end_session(99999)
    assert result is False

@pytest.mark.asyncio
async def test_handle_game_started(game_manager, mock_channel):
    """게임 시작 이벤트 처리 테스트"""
    channel_id = 67890
    user_id = 12345
    
    # 채널 mock 설정
    game_manager.bot.get_channel.return_value = mock_channel
    
    # 게임 시작 이벤트 생성
    event = EventGameStarted(
        user_id=user_id,
        channel_id=channel_id
    )
    
    # 이벤트 처리
    await game_manager.handle_game_started(event)
    
    # 채널 메시지 전송 확인
    mock_channel.send.assert_called_once()
    assert str(user_id) in mock_channel.send.call_args[0][0]
    assert str(channel_id) in mock_channel.send.call_args[0][0]

@pytest.mark.asyncio

@pytest.mark.asyncio
async def test_handle_game_error(game_manager, mock_channel):
    """게임 에러 이벤트 처리 테스트"""
    channel_id = 67890
    error_info = "Test error message"
    
    # 채널 mock 설정
    game_manager.bot.get_channel.return_value = mock_channel
    
    # 에러 이벤트 생성
    event = EventError(
        user_id=12345,
        channel_id=channel_id,
        error_info=error_info,
        severity="HIGH"
    )
    
    # 이벤트 처리
    await game_manager.handle_game_error(event)
    
    # 에러 메시지 전송 확인
    mock_channel.send.assert_called_once()
    assert error_info in mock_channel.send.call_args[0][0]

@pytest.mark.asyncio
async def test_send_game_message(game_manager, mock_channel):
    """게임 메시지 전송 테스트"""
    channel_id = 67890
    
    # 채널 mock 설정
    game_manager.bot.get_channel.return_value = mock_channel
    mock_message = Mock(spec=discord.Message)
    mock_channel.send.return_value = mock_message
    
    # 메시지 전송
    result = await game_manager.send_game_message(channel_id)
    
    # 결과 확인
    mock_channel.send.assert_called_once()
    assert isinstance(mock_channel.send.call_args[1]['embed'], discord.Embed)
    assert result == mock_message

@pytest.mark.asyncio
async def test_send_game_message_no_channel(game_manager):
    """채널이 없는 경우의 게임 메시지 전송 테스트"""
    channel_id = 67890
    game_manager.bot.get_channel.return_value = None
    
    with pytest.raises(GameError, match=f"Cannot find channel with ID {channel_id}"):
        await game_manager.send_game_message(channel_id)

@pytest.mark.asyncio
async def test_send_game_message_forbidden(game_manager, mock_channel):
    """권한이 없는 경우의 게임 메시지 전송 테스트"""
    channel_id = 67890
    game_manager.bot.get_channel.return_value = mock_channel
    mock_channel.send.side_effect = discord.Forbidden(Mock(), "No permission")
    
    with pytest.raises(GameError, match="Bot doesn't have permission"):
        await game_manager.send_game_message(channel_id)

@pytest.mark.asyncio
async def test_event_subscription(game_manager):
    """이벤트 구독 테스트"""
    assert EventType.GAME_STARTED in game_manager.event_bus.subscribers
    assert EventType.GAME_ERROR in game_manager.event_bus.subscribers
    assert game_manager.handle_game_started in game_manager.event_bus.subscribers[EventType.GAME_STARTED]
    assert game_manager.handle_game_error in game_manager.event_bus.subscribers[EventType.GAME_ERROR]

def test_multiple_game_sessions(game_manager):
    """여러 게임 세션 관리 테스트"""
    sessions_data = [
        (12345, 67890),
        (23456, 78901),
        (34567, 89012)
    ]
    
    async def create_sessions():
        for user_id, channel_id in sessions_data:
            result = await game_manager.start_session(user_id, channel_id)
            assert result in [EventType.GAME_STARTED, EventType.CREATE_PLAYER]
    
    # 여러 세션 생성
    asyncio.run(create_sessions())
    
    # 세션 수 확인
    assert len(game_manager.sessions) == len(sessions_data)
    
    # 각 세션 정보 확인
    for user_id, channel_id in sessions_data:
        assert user_id in game_manager.sessions
        assert game_manager.sessions[user_id].channel_id == channel_id
# ===== test_game_session.py =====
import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from dg01.game_session import GameSession
from dg01.event_bus import EventBus
from dg01.game_events import (
    GameState,
    EventType,
    EventGameStarted,
    EventError,
    EventGameCleanup
)
from dg01.errors import GameError
from dg01.data_manager import DataManager


@pytest.fixture
def event_bus():
    """이벤트 버스 fixture"""
    bus = EventBus()
    bus.publish = AsyncMock()
    return bus

@pytest.fixture
def game_session(event_bus):
    """게임 세션 fixture"""
    session = GameSession(
        user_id=12345,
        channel_id=67890,
        event_bus=event_bus,
        data_manager=DataManager()
    )
    session.data_manager.get_or_create_user_data = AsyncMock()
    session.data_manager.update_user_data = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_game_session_initialization(game_session):
    """게임 세션 초기화 테스트"""
    assert game_session.user_id == 12345
    assert game_session.channel_id == 67890
    assert game_session.state == GameState.WAITING
    assert game_session.tick_rate == 1.0
    assert game_session.message_id is None

@pytest.mark.asyncio
async def test_start_game(game_session):
    """게임 시작 테스트"""
    await game_session.start_game()
    
    assert game_session.state == GameState.PLAYING
    assert hasattr(game_session, 'last_update')
    assert hasattr(game_session, 'update_task')
    
    # GameStarted 이벤트가 발행되었는지 확인
    game_session.event_bus.publish.assert_called_once()
    event = game_session.event_bus.publish.call_args[0][0]
    assert isinstance(event, EventGameStarted)
    assert event.user_id == game_session.user_id
    assert event.channel_id == game_session.channel_id

@pytest.mark.asyncio
async def test_start_game_already_started(game_session):
    """이미 시작된 게임 시작 시도 테스트"""
    game_session.state = GameState.PLAYING
    
    with pytest.raises(GameError, match="Game already started"):
        await game_session.start_game()

@pytest.mark.asyncio
async def test_update_loop_basic_functionality(game_session):
    """업데이트 루프 기본 기능 테스트"""
    # 게임 로직 모의
    mock_events = [Mock(type=EventType.UPDATE_PLAYER, data={"user_id": 12345})]
    game_session.game_logic.update = Mock(return_value=mock_events)
    
    # 게임 시작
    await game_session.start_game()
    
    # 한 틱 실행
    await asyncio.sleep(1.1)
    
    # 업데이트가 실행되었는지 확인
    assert game_session.game_logic.update.called
    assert game_session.data_manager.get_or_create_user_data.called

    # 정리
    await game_session.cleanup()

@pytest.mark.asyncio
async def test_cleanup(game_session):
    """게임 세션 정리 테스트"""
    # 게임 시작
    await game_session.start_game()
    
    # 정리 실행
    await game_session.cleanup()
    
    assert game_session.state == GameState.FINISHED
    assert not game_session.update_task or game_session.update_task.done()
    
    # GameCleanup 이벤트가 발행되었는지 확인
    cleanup_event_call = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventGameCleanup)
    ]
    assert len(cleanup_event_call) == 1

@pytest.mark.asyncio
async def test_handle_error_game_error(game_session):
    """GameError 처리 테스트"""
    game_session.state = GameState.PLAYING
    error = GameError("Test game error")
    
    await game_session.handle_error(error)
    
    assert game_session.state == GameState.PAUSED
    
    # 에러 이벤트가 발행되었는지 확인
    error_event_call = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventError)
    ]
    assert len(error_event_call) == 1
    error_event = error_event_call[0][0][0]
    assert error_event.severity == 'error'

@pytest.mark.asyncio
async def test_handle_error_unknown_error(game_session):
    """알 수 없는 에러 처리 테스트"""
    game_session.state = GameState.PLAYING
    error = Exception("Unknown error")
    
    await game_session.handle_error(error)
    
    assert game_session.state == GameState.ERROR
    
    # 에러 이벤트가 발행되었는지 확인
    error_event_call = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventError)
    ]
    assert len(error_event_call) == 1
    error_event = error_event_call[0][0][0]
    assert error_event.severity == 'unknown'

@pytest.mark.asyncio
async def test_update_loop_error_handling(game_session):
    """업데이트 루프 에러 처리 테스트"""
    # 게임 로직이 예외를 발생시키도록 설정
    game_session.game_logic.update = Mock(side_effect=Exception("Test error"))
    
    # 게임 시작
    await game_session.start_game()
    
    # 에러가 발생할 때까지 대기
    await asyncio.sleep(1.1)
    
    # 게임이 에러 상태가 되었는지 확인
    assert game_session.state == GameState.ERROR
    
    # 에러 이벤트가 발행되었는지 확인
    error_event_calls = [
        call for call in game_session.event_bus.publish.call_args_list 
        if isinstance(call[0][0], EventError)
    ]
    assert len(error_event_calls) > 0
