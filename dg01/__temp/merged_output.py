from abc import ABC
from dataclasses import dataclass
from dataclasses import dataclass, field
from dataclasses import field
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
from dg01.data_manager import DataManager
from dg01.digimon_battle import BattleHandler
from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx, get_battle_chance, get_config_val
from dg01.digimon_config import STAGES, get_stage_config
from dg01.digimon_config import get_stage_config
from dg01.digimon_data import DigimonDataFields
from dg01.digimon_logic import DigimonLogic, STAGES
from dg01.digimon_quiz import QuizHandler
from dg01.errors import setup_logger
from dg01.errors import setup_logger, GameError
from dg01.event_bus import EventBus
from dg01.game_events import EventType, EventBase
from dg01.game_events import EventType, EventBase, EventQuizPassNeeded, EventBattleWin, EventBattleLose, EventBattleItemGet, EventUpdateDashboard
from dg01.game_events import EventType, EventBattleWin, EventBattleLose, EventBattleItemGet
from dg01.game_events import EventType, EventQuizPassNeeded, EventBattleWin, EventBattleLose, EventBattleItemGet
from dg01.game_events import GameState
from dg01.game_events import GameState, EventType, EventBase, EventUpdateDashboard
from dg01.game_manager import GameManager
from dg01.game_session import GameSession
from dg01.utils import get_google_sheet_df
from digimon_config import update_digimon_config_csv
from discord import ButtonStyle, Interaction
from discord.ext import commands
from discord.ui import Button, View
from discord.ui import Modal, TextInput
from enum import Enum
from io import StringIO
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict
from typing import Dict, Any
from typing import Dict, List
from typing import Dict, Type
from typing import Optional
from typing import Optional, Dict, Any
from typing import Optional, Dict, Any, List
from typing import Optional, Dict, Any, List, NamedTuple
from typing import TypeVar, Generic
from urllib.parse import urlparse, parse_qs
import aiosqlite
import argparse
import asyncio
import discord
import json
import logging
import os
import pandas as pd
import random
import requests
import sqlite3
import sys
import traceback

# Generated on 2024-12-17 18:33:22

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

# ===== digimon_battle.py =====
from dataclasses import dataclass
from typing import Optional
import random
import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.game_events import EventType, EventBattleWin, EventBattleLose, EventBattleItemGet


logger = setup_logger(__name__)


class BattleView:
    """전투 관련 출력을 담당하는 클래스"""
    def __init__(self, switch=1):
        self.switch = switch

    async def send_battle_win(self, channel: discord.TextChannel, user_id: int, battles_won: int, battles_lost: int) -> None:
        """전투 승리 메시지 전송"""
        embed = discord.Embed(
            title="⚔️ 전투 승리!",
            description="전투에서 승리했습니다!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 전투 기록",
            value=f"총 전적: {battles_won}승 {battles_lost}패",
            inline=False
        )
        
        if self.switch:
            await channel.send(embed=embed)

    async def send_battle_item_get(self, channel: discord.TextChannel, user_id: int, item_id: int) -> None:
        """전투 아이템 획득 메시지 전송"""
        embed = discord.Embed(
            title="🎁 아이템 획득!",
            description="전투 승리로 특별한 아이템을 획득했습니다!",
            color=discord.Color.gold()
        )
        
        item_descriptions = {
            1: "강화된 방어구",
            2: "공격력 증가 아이템",
            3: "회복 아이템"
        }
        
        item_description = item_descriptions.get(item_id, "알 수 없는 아이템")
        embed.add_field(
            name="획득한 아이템",
            value=item_description,
            inline=False
        )
        
        if self.switch:
            await channel.send(embed=embed)

    async def send_battle_lose(self, channel: discord.TextChannel, user_id: int, 
                             count_lost: int, battles_won: int, battles_lost: int, 
                             remaining_count: int) -> None:
        """전투 패배 메시지 전송"""
        embed = discord.Embed(
            title="💔 전투 패배",
            description=f"전투에서 패배했습니다... {count_lost:,} 개체를 잃었습니다.\n!치료 해주세요.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="📊 전투 기록",
            value=f"총 전적: {battles_won}승 {battles_lost}패",
            inline=False
        )
        
        embed.add_field(
            name="💪 현재 상태",
            value=f"남은 개체 수: {remaining_count:,}",
            inline=False
        )

        if self.switch:
            await channel.send(embed=embed)


class BattleHandler:
    """전투 관련 로직을 처리하는 클래스"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = BattleView(switch=1)
    
    async def handle_battle_win(self, event: EventBattleWin, battles_won: int, battles_lost: int) -> None:
        """전투 승리 처리"""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found for battle win event")
            return

        await self.view.send_battle_win(
            channel=channel,
            user_id=event.user_id,
            battles_won=battles_won,
            battles_lost=battles_lost
        )

    async def handle_battle_item_get(self, event: EventBattleItemGet) -> None:
        """전투 아이템 획득 처리"""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found for battle item event")
            return

        await self.view.send_battle_item_get(
            channel=channel,
            user_id=event.user_id,
            item_id=event.obtained_item_id
        )

    async def handle_battle_lose(self, event: EventBattleLose, 
                               battles_won: int, battles_lost: int, 
                               remaining_count: int) -> None:
        """전투 패배 처리"""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found for battle lose event")
            return

        await self.view.send_battle_lose(
            channel=channel,
            user_id=event.user_id,
            count_lost=event.count_lost,
            battles_won=battles_won,
            battles_lost=battles_lost,
            remaining_count=remaining_count
        )
# ===== digimon_config.py =====
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, NamedTuple

import pandas as pd

from dg01.utils import get_google_sheet_df
from dg01.errors import setup_logger


logger = setup_logger(__name__)


DIGIMON_CNOFIG_URL = "https://docs.google.com/spreadsheets/d/1_VOmKB_iGmPYKOpLzysrZx9FBeSAoTLifbn8PS793rU/edit?usp=sharing"
DIGIMON_CONFIG_CSV_PATH = "digimon_config.csv"
dfp_digimon_config = pd.read_csv(DIGIMON_CONFIG_CSV_PATH, encoding='utf-8-sig')


def validate_dfp_digimon_config(dfp_digimon_config):
    assert dfp_digimon_config.shape[0] > 6
    assert len(dfp_digimon_config['stage_idx'].unique()) == dfp_digimon_config.shape[0]


def update_digimon_config_csv():
    dfp_digimon_config = get_google_sheet_df(sheet_url=DIGIMON_CNOFIG_URL)
    validate_dfp_digimon_config(dfp_digimon_config=dfp_digimon_config)
    dfp_digimon_config.to_csv(DIGIMON_CONFIG_CSV_PATH, encoding="utf-8-sig", index=False)
    print(dfp_digimon_config.head())


validate_dfp_digimon_config(dfp_digimon_config=dfp_digimon_config)


STAGES = {  # stage_idx: stage_name
    r['stage_idx']: r['stage_name'] 
    for r 
    in dfp_digimon_config[["stage_idx", "stage_name"]].to_dict(orient="records")
}
STAGE_CONFIG = dfp_digimon_config.to_dict(orient="records")
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
    global dfp_digimon_config
    _dfp_digimon_config = dfp_digimon_config.query(f"stage_idx == {stage_idx}")
    assert _dfp_digimon_config.shape[0] == 1
    return _dfp_digimon_config.to_dict(orient="records")[0]

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

def get_config_val(stage_idx: int, field_name: str):
    return get_stage_config(stage_idx)[field_name]
# ===== digimon_data.py =====
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, NamedTuple


@dataclass
class DigimonDataFields:
    """사용자 데이터 필드 정의"""
    user_id: int = field(default=-1, metadata={"primary_key": True, "type": "INTEGER", "default": -1})
    channel_id: int = field(default=-1, metadata={"type": "INTEGER", "nullable": False, "default": -1})
    stage_idx: int = field(default=0, metadata={"type": "INTEGER", "nullable": False, "default": 0})
    count: int = field(default=0, metadata={"type": "INTEGER", "default": 0})  # 진화 요건이 충족되었으나, 퀴즈 풀이가 필요한 상황
    quiz_pass_needed: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    quiz_question: str = field(default="", metadata={"type": "TEXT", "nullable": False, "default": ""})
    quiz_answer: str = field(default="", metadata={"type": "TEXT", "nullable": False, "default": ""})
    quiz_published: int = field(default=0, metadata={"type": "INTEGER", "default": 0})  # 퀴즈를 출제했음. 정해진 시간내에 답을 하지 않으면 이 값을 0으로 만들고 퀴즈를 다시 출제
    battles_won: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    battles_lost: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    last_cheer: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
    is_copying: int = field(default=0, metadata={"type": "INTEGER", "default": 0})
    last_played: Optional[str] = field(default=None, metadata={"type": "TEXT", "nullable": True, "default": ""})
# ===== digimon_logic.py =====
import random
from typing import Dict, Any

from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx, get_battle_chance, get_config_val
from dg01.errors import setup_logger
from dg01.digimon_data import DigimonDataFields
from dg01.game_events import (
    EventType, 
    EventQuizPassNeeded,
    EventBattleWin,
    EventBattleLose,
    EventBattleItemGet
)


logger = setup_logger(__name__)


class DigimonLogic(DigimonDataFields):
    """디지몬 게임의 핵심 로직을 관리하는 클래스"""
    def __init__(self, user_id: int, channel_id: int, data: Dict[str, Any] = None, **kwargs):
        # data dict가 제공되면 그것을 사용하고, 아니면 kwargs 사용
        init_data = data if data is not None else kwargs
        init_data['user_id'] = user_id
        init_data['channel_id'] = channel_id
        
        # DigimonDataFields의 모든 필드에 대해 초기화
        for field_name in DigimonDataFields.__dataclass_fields__:
            # data에 해당 필드가 있으면 그 값을 사용, 없으면 기본값 사용
            default_value = DigimonDataFields.__dataclass_fields__[field_name].default
            value = init_data.get(field_name, default_value)
            setattr(self, field_name, value)

    def update(self, delta_time):
        print(f"=== {delta_time:.3f} ===")
        print(f"====== {self.__dict__=} ===============")

        update_events = []

        # check copy
        events = self.copy_digimon(delta_time=delta_time)
        if events:
            update_events.extend(events)
        
        # check evolution
        events = self.check_evolution()
        if events:
            update_events.extend(events)
        
        # check battle        
        events = self.process_battle()
        if events:
            update_events.extend(events)

        # check news

        # check random message

        return update_events
    
    def copy_digimon(self, delta_time):
        if self.is_copying == 1:
            new_count = self.count + (STAGE_CONFIG[self.stage_idx]["copy_rate"] * delta_time)
            self.count = int(new_count)
        else:
            pass
    
        return None
    
    def check_evolution(self):
        def _get_random_quiz():
            question = "1 + 1"
            answer = "2"
            return question, answer

        if self.stage_idx == max(STAGES.keys()):
            return None
        
        if self.count >= STAGE_CONFIG[self.stage_idx]["evolution_count"] and self.quiz_published == 0:
            self.quiz_pass_needed = 1
            self.quiz_published == 1
            self.is_copying = 0
            self.quiz_question, self.quiz_answer = _get_random_quiz()
            self.quiz_published = 1
            return [EventQuizPassNeeded(
                user_id=self.user_id,
                channel_id=self.channel_id,
                quiz_question=self.quiz_question,
                quiz_answer=self.quiz_answer
            )]

        """
        if self.is_copying == 1 and self.count >= STAGE_CONFIG[self.stage_idx]["evolution_count"]:
            self.quiz_pass_needed = 1
            self.is_copying = 0
            if self.quiz_published == 1:
                return None
            else:
                self.quiz_question, self.quiz_answer = _get_random_quiz()
                self.quiz_published = 1
                return [EventQuizPassNeeded(
                    user_id=self.user_id,
                    channel_id=self.channel_id,
                    quiz_question=self.quiz_question,
                    quiz_answer=self.quiz_answer
                )]
        else:
            return None
        """
        
    def start_copying(self):
        if self.quiz_pass_needed == 1:
            pass
        else:
            self.is_copying = 1

        return None

    def get_quiz_prepared(self):
        if self.quiz_pass_needed == 1 and self.quiz_question != "" and self.quiz_answer != "":
            return self.quiz_question, self.quiz_answer
        else:
            return None, None

    def mark_quiz_passed(self):
        self.quiz_pass_needed = 0
        self.quiz_published = 0
        self.quiz_question = ""
        self.quiz_answer = ""
        self.is_copying = 1
        self.stage_idx = get_next_stage_idx(self.stage_idx)

    def mark_quiz_failed(self):
        self.quiz_published = 0  # 또 다시 퀴즈를 내야한다.
        self.quiz_question = ""
        self.quiz_answer = ""

    def mark_quie_timeout(self):
        self.quiz_published = 0  # 또 다시 퀴즈를 내야한다.
        self.quiz_question = ""
        self.quiz_answer = ""

    def start_copying(self):
        if self.quiz_pass_needed == 1:
            pass
        else:
            self.is_copying = 1

        return None
    
    def process_battle(self):
        battle_chance = get_config_val(self.stage_idx, "battle_chance")
        battle_win_ratio_default = get_config_val(self.stage_idx, "battle_win_ratio_default")
        battle_win_ratio_w_item = get_config_val(self.stage_idx, "battle_win_ratio_w_item")
        battle_win_reward_chance = get_config_val(self.stage_idx, "battle_win_reward_chance")
        battle_lose_del_ratio = get_config_val(self.stage_idx, "battle_lose_del_ratio")
        
        f_has_item = 0
        f_has_cheer = 0

        if self.is_copying == 1 and random.random() <  battle_chance:
            # basee win ratio
            win_ratio = battle_win_ratio_w_item if f_has_item else battle_win_ratio_default

            # + win ratio
            win_ratio = (win_ratio + battle_win_ratio_default * 0.2) if f_has_cheer else win_ratio

            if random.random() < win_ratio:
                # win case  
                self.battles_won += 1
                if random.random() < battle_win_reward_chance:
                    # win & item get
                    return [
                        EventBattleWin(user_id=self.user_id, channel_id=self.channel_id),
                        EventBattleItemGet(user_id=self.user_id, channel_id=self.channel_id)
                    ]
                else:
                    return [EventBattleWin(user_id=self.user_id, channel_id=self.channel_id)]
            else:
                # lose case
                self.battles_lost += 1
                count_lost = int(self.count * battle_lose_del_ratio)
                self.count -= count_lost
                self.is_copying = 0
                return [EventBattleLose(user_id=self.user_id, channel_id=self.channel_id, count_lost=count_lost)]
        else:
            # no battle
            pass
            
# ===== digimon_quiz.py =====

import asyncio
from typing import Optional

import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
from discord import ButtonStyle, Interaction
from discord.ui import Button, View




class QuizModal(Modal):
    def __init__(self, question: str, correct_answer: str, callback):
        super().__init__(title="진화 퀴즈")
        self.correct_answer = correct_answer
        self.callback = callback
        
        # Add question display
        self.add_item(
            TextInput(
                label="문제",
                default=question,
                style=discord.TextStyle.paragraph,
                required=False
            )
        )
        
        # Add answer input
        self.add_item(
            TextInput(
                label="답변",
                placeholder="답을 입력하세요",
                style=discord.TextStyle.short,
                required=True,
                max_length=100
            )
        )

    async def on_submit(self, interaction: Interaction):
        answer = self.children[1].value.strip()
        is_correct = answer.lower() == self.correct_answer.lower()
        
        if is_correct:
            embed = discord.Embed(
                title="🎉 정답입니다!",
                description="축하합니다! 다음 단계로 진화합니다!",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ 오답입니다!",
                description="다시 한번 도전해보세요!",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)
        await self.callback(interaction.user.id, interaction.channel_id, answer)

class QuizView(View):
    def __init__(self, question: str, correct_answer: str, callback, timeout=30):
        super().__init__(timeout=timeout)
        self.question = question
        self.correct_answer = correct_answer
        self.callback = callback
        
        # Add answer button
        self.add_item(Button(
            label="답변하기",
            style=ButtonStyle.primary,
            custom_id="answer_quiz"
        ))
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.data["custom_id"] == "answer_quiz":
            modal = QuizModal(
                question=self.question,
                correct_answer=self.correct_answer,
                callback=self.callback
            )
            await interaction.response.send_modal(modal)
        return True


# Update QuizHandler class
class QuizHandler:
    def __init__(self, bot: commands.Bot, game_manager=None):
        self.bot = bot
        self.game_manager = game_manager
        self.active_quizzes = {}

    async def start_quiz(self, channel: discord.TextChannel, user_id: int,
                        question: str, answer: str, timeout_callback) -> bool:
        """새 퀴즈를 시작합니다."""
        if user_id in self.active_quizzes:
            embed = discord.Embed(
                title="⚠️ 진행 중인 퀴즈",
                description=f"<@{user_id}> 이미 진행 중인 퀴즈가 있습니다!",
                color=discord.Color.orange()
            )
            await channel.send(embed=embed)
            return False

        # Create and send quiz embed with button
        quiz_embed = discord.Embed(
            title="🎯 진화 퀴즈!",
            description="다음 단계로 진화하기 위한 퀴즈입니다!",
            color=discord.Color.blue()
        )
        
        quiz_view = QuizView(
            question=question,
            correct_answer=answer,
            callback=self.check_answer,
            timeout=30
        )
        
        message = await channel.send(embed=quiz_embed, view=quiz_view)
        
        # Set up timeout handling
        timeout_task = asyncio.create_task(self._handle_timeout(
            user_id, channel, timeout_callback, message
        ))

        self.active_quizzes[user_id] = {
            'answer': answer,
            'channel_id': channel.id,
            'quiz_task': timeout_task,
            'message': message
        }
        
        return True

    async def _handle_timeout(self, user_id: int, channel: discord.TextChannel,
                            timeout_callback, message: discord.Message) -> None:
        """퀴즈 타임아웃을 처리합니다."""
        await asyncio.sleep(30)
        if user_id in self.active_quizzes:
            await self.end_quiz(user_id)
            
            timeout_embed = discord.Embed(
                title="⏰ 시간 초과",
                description=f"<@{user_id}> 시간이 초과되었습니다! 다시 도전해보세요.",
                color=discord.Color.red()
            )
            
            # Disable the button view
            try:
                await message.edit(embed=timeout_embed, view=None)
            except discord.NotFound:
                pass
                
            await timeout_callback(user_id)

    async def check_answer(self, user_id: int, channel_id: int, answer: str) -> Optional[bool]:
        """사용자의 답변을 확인합니다."""
        quiz_info = self.active_quizzes.get(user_id)
        if not quiz_info or quiz_info['channel_id'] != channel_id:
            return None

        quiz_info['quiz_task'].cancel()
        is_correct = answer.strip().lower() == quiz_info['answer'].lower()

        session = await self.game_manager.get_session(user_id, channel_id)
        if is_correct:
            session.digimon.mark_quiz_passed()
        else:
            session.digimon.mark_quiz_failed()

        # Disable the button view
        try:
            await quiz_info['message'].edit(view=None)
        except discord.NotFound:
            pass
            
        await self.end_quiz(user_id)
        return is_correct

    async def end_quiz(self, user_id: int) -> None:
        """진행 중인 퀴즈를 종료합니다."""
        if user_id in self.active_quizzes:
            del self.active_quizzes[user_id]
# ===== digimon_quiz__old.py =====
import asyncio
from typing import Optional

import discord
from discord.ext import commands


class QuizView:
    """퀴즈 관련 UI를 관리하는 클래스"""

    @staticmethod
    async def send_quiz(channel: discord.TextChannel, user_id: int, question: str) -> None:
        """퀴즈 출제 메시지를 전송합니다."""
        quiz_embed = discord.Embed(
            title="🎯 진화 퀴즈!",
            description=f"다음 단계로 진화하기 위한 퀴즈입니다!\n\n**문제**: {question}",
            color=discord.Color.blue()
        )
        quiz_embed.add_field(
            name="답변 방법",
            value="채팅으로 답을 입력해주세요! (30초 안에 답변해야 합니다)",
            inline=False
        )

        await channel.send(embed=quiz_embed)

    @staticmethod
    async def send_timeout(channel: discord.TextChannel, user_id: int) -> None:
        """퀴즈 시간 초과 메시지를 전송합니다."""
        await channel.send(f"<@{user_id}> 시간이 초과되었습니다! 다시 도전해보세요.")

    @staticmethod
    async def send_already_active(channel: discord.TextChannel, user_id: int) -> None:
        """이미 진행 중인 퀴즈가 있다는 메시지를 전송합니다."""
        await channel.send(f"<@{user_id}> 이미 진행 중인 퀴즈가 있습니다!")

    @staticmethod
    async def send_correct_answer(channel: discord.TextChannel) -> None:
        """정답 메시지를 전송합니다."""
        success_embed = discord.Embed(
            title="🎉 정답입니다!",
            description="축하합니다! 다음 단계로 진화합니다!",
            color=discord.Color.green()
        )
        await channel.send(embed=success_embed)

    @staticmethod
    async def send_wrong_answer(channel: discord.TextChannel) -> None:
        """오답 메시지를 전송합니다."""
        fail_embed = discord.Embed(
            title="❌ 오답입니다!",
            description="다시 한번 도전해보세요!",
            color=discord.Color.red()
        )
        await channel.send(embed=fail_embed)


class QuizHandler:
    """퀴즈 관련 로직을 처리하는 클래스"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = QuizView()
        self.active_quizzes = {}  # user_id: quiz_info

    async def start_quiz(self, channel: discord.TextChannel, user_id: int,
                        question: str, answer: str, timeout_callback) -> bool:
        """새 퀴즈를 시작합니다."""
        if user_id in self.active_quizzes:
            await self.view.send_already_active(channel, user_id)
            return False

        await self.view.send_quiz(channel, user_id, question)

        timeout_task = asyncio.create_task(self._handle_timeout(
            user_id, channel, timeout_callback
        ))

        self.active_quizzes[user_id] = {
            'answer': answer,
            'channel_id': channel.id,
            'quiz_task': timeout_task
        }
        return True

    async def _handle_timeout(self, user_id: int, channel: discord.TextChannel,
                            timeout_callback) -> None:
        """퀴즈 타임아웃을 처리합니다."""
        await asyncio.sleep(30)
        if user_id in self.active_quizzes:
            await self.end_quiz(user_id)
            await self.view.send_timeout(channel, user_id)
            await timeout_callback(user_id)

    async def check_answer(self, user_id: int, channel_id: int,
                          answer: str) -> Optional[bool]:
        """사용자의 답변을 확인합니다."""
        quiz_info = self.active_quizzes.get(user_id)
        if not quiz_info or quiz_info['channel_id'] != channel_id:
            return None

        quiz_info['quiz_task'].cancel()
        is_correct = answer.strip().lower() == quiz_info['answer'].lower()
        await self.end_quiz(user_id)

        if is_correct:
            await self.view.send_correct_answer(
                self.bot.get_channel(channel_id)
            )
        else:
            await self.view.send_wrong_answer(
                self.bot.get_channel(channel_id)
            )

        return is_correct

    async def end_quiz(self, user_id: int) -> None:
        """진행 중인 퀴즈를 종료합니다."""
        if user_id in self.active_quizzes:
            del self.active_quizzes[user_id]
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

# ===== game_bot.py =====




# ===== game_cog.py =====

# ===== game_events.py =====
from dataclasses import field
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Type
from abc import ABC
from typing import TypeVar, Generic


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


class EventType(Enum):
    GAME_STARTED = "game_started"
    GAME_CLEANUP = "game_cleanup"
    GAME_ERROR = "game_error"
    CREATE_PLAYER = "create_player"
    UPDATE_PLAYER = "update_player"
    QUIZ_PASS_NEEDED = "quiz_pass_needed"
    BATTLE_WIN = "battle_win"
    BATTLE_LOSE = "battle_lose"
    BATTLE_ITEM_GET = "battle_item_get"
    UPDATE_DASHBOARD = "update_dashboard"
    EVOLVED = "evolved"

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

@dataclass
class EventQuizPassNeeded(EventBase):
    quiz_question: str = ""
    quiz_answer: str = ""
    event_type: EventType = EventType.QUIZ_PASS_NEEDED

@dataclass
class EventBattleWin(EventBase):
    event_type: EventType = EventType.BATTLE_WIN

@dataclass
class EventBattleLose(EventBase):
    count_lost: int = 0  # 전투 패비로 잃게된 개체수
    event_type: EventType = EventType.BATTLE_LOSE

@dataclass
class EventBattleItemGet(EventBase):
    obtained_item_id: int = -1  # 전투 승리 후 확률적으로 얻게된 아이템의 식별자
    event_type: EventType = EventType.BATTLE_ITEM_GET

@dataclass
class EventUpdateDashboard(EventBase):
    event_type: EventType =  EventType.UPDATE_DASHBOARD

@dataclass
class EventEvolved(EventBase):
    event_type: EventType = EventType.EVOLVED
# ===== game_manager.py =====
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

# ===== game_session.py =====
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import discord
from discord.ext import commands

from dg01.errors import setup_logger, GameError
from dg01.game_events import GameState, EventType, EventBase, EventUpdateDashboard
from dg01.digimon_logic import DigimonLogic, STAGES
from dg01.digimon_config import get_stage_config
from dg01.event_bus import EventBus


logger = setup_logger(__name__)


class GameSession:
    def __init__(self, user_id: int, channel_id: int, event_bus: EventBus, data: Dict[str, Any] = None):
        self.user_id = user_id
        self.user_name = None
        self.channel_id = channel_id
        self.digimon = DigimonLogic(user_id=user_id, channel_id=channel_id, data=data)
        self.state = GameState.WAITING
        self.event_bus = event_bus
        self.tick_rate = 1.0

        self.dashboard_message = None
        self.last_dashboard_update = 0
        self.dashboard_update_interval = 1.0  # 초단위 업데이트 간격

        self.current_image_file = None  # 현재 디지몬 이미지 파일 저장용

    async def start_game(self):
        if self.state != GameState.WAITING:
            raise GameError("Game already started")

        self.state = GameState.PLAYING
        self.last_update = asyncio.get_running_loop().time()
        self.update_task = asyncio.create_task(self.update_loop())
        self.digimon.start_copying()

    def set_user_name(self, user_name):
        if user_name:
            self.user_name = user_name
        else:
            pass
    
    def set_dashboard_message(self, dashboard_message):
        self.dashboard_message = dashboard_message

    def set_channel_id(self, channel_id):
        self.digimon.channel_id = channel_id

    async def update_loop(self):
        try:
            while self.state == GameState.PLAYING:
                current_time = asyncio.get_running_loop().time()
                delta_time = current_time - self.last_update
                
                # 게임 로직 업데이트
                events = self.digimon.update(delta_time)
                if events:
                    for event in events:
                        await self.event_bus.publish(event)
                
                # 대시보드 업데이트 체크
                if (self.dashboard_message and 
                    current_time - self.last_dashboard_update >= self.dashboard_update_interval):
                    await self.event_bus.publish(
                        EventUpdateDashboard(
                            user_id=self.user_id,
                            channel_id=self.channel_id
                        )
                    )
                    self.last_dashboard_update = current_time
                
                self.last_update = current_time
                
                # 다음 틱까지 대기
                next_update = self.last_update + (1.0 / self.tick_rate)
                sleep_time = max(0, next_update - asyncio.get_running_loop().time())
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            await self.cleanup()
        except Exception as e:
            raise e
            # await self.handle_error(e)

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

            # 게임 상태를 FINISHED로 변경
            self.state = GameState.FINISHED

            logger.info(f"Cleaned up game session for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error during cleanup for user {self.user_id}: {str(e)}")

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
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
            print(error_info)

            # GameError와 그 외 예외를 구분하여 처리
            if isinstance(error, GameError):
                logger.error(f"Game Error: {error_info}")
            else:
                logger.critical(f"Unknown Error in game session: {error_info}")

        except Exception as e:
            logger.critical(f"Error in error handler: {str(e)}")
            if ctx:
                try:
                    await ctx.send("An unexpected error occurred in the error handler.")
                except:
                    pass

# ===== main.py =====
import json
import argparse
from pathlib import Path

import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.game_manager import GameManager
from digimon_config import update_digimon_config_csv

logger = setup_logger(__name__)


class GameBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.game_manager = GameManager(self)

    async def setup_hook(self):
        await self.add_cog(self.game_manager)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("봇에 필요한 권한이 없습니다.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("존재하지 않는 명령어입니다.")
        else:
            print(f'에러 발생: {error}')

    async def on_message(self, message):
        if message.author.bot:
            return

        # await self.game_manager.handle_quiz_message(message)
        await self.process_commands(message)


def parse_args():
    parser = argparse.ArgumentParser(description='Digimon Game Bot')
    parser.add_argument('--update_config', action='store_true',
                       help='Update digimon config from Google Sheets')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    if args.update_config:
        logger.info("Updating digimon config from Google Sheets...")
        try:
            update_digimon_config_csv()
        except Exception as e:
            logger.info("Config update failed with", e)
        else:
            logger.info("Config update completed")

    with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
        token = json.load(f)['discord_token']

    bot = GameBot()

    """
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        
        await bot.game_manager.handle_quiz_message(message)
        await bot.process_commands(message)
    """
    bot.run(token)

# ===== utils.py =====
import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs
from io import StringIO


def download_google_sheet(sheet_url, output_filename='output.csv'):
    """
    구글 스프레드시트 URL에서 데이터를 다운로드하여 CSV 파일로 저장합니다.
    
    Parameters:
        sheet_url (str): 구글 스프레드시트 공유 URL
        output_filename (str): 저장할 CSV 파일명 (기본값: 'output.csv')
    """
    try:
        # URL이 올바른 구글 스프레드시트 주소인지 확인
        if 'docs.google.com/spreadsheets' not in sheet_url:
            raise ValueError('올바른 구글 스프레드시트 URL이 아닙니다.')
            
        # URL에서 스프레드시트 ID 추출
        parsed_url = urlparse(sheet_url)
        if 'spreadsheets/d/' in sheet_url:
            sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
        else:
            query_params = parse_qs(parsed_url.query)
            sheet_id = query_params.get('id', [None])[0]
            
        if not sheet_id:
            raise ValueError('스프레드시트 ID를 찾을 수 없습니다.')
        
        # CSV 다운로드 URL 생성
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        
        # 데이터 다운로드
        response = requests.get(csv_export_url)
        response.raise_for_status()  # HTTP 에러 체크
        
        # CSV 파일로 저장
        with open(output_filename, 'wb') as f:
            f.write(response.content)
            
        print(f'데이터가 성공적으로 {output_filename}에 저장되었습니다.')
        
        # pandas로 데이터 읽기 (옵션)
        df = pd.read_csv(output_filename)
        return df.head()
        
    except requests.exceptions.RequestException as e:
        print(f'다운로드 중 오류가 발생했습니다: {e}')
    except ValueError as e:
        print(f'URL 처리 중 오류가 발생했습니다: {e}')
    except Exception as e:
        print(f'예상치 못한 오류가 발생했습니다: {e}')


def get_google_sheet_df(sheet_url, sheet_name=None):
    """
    구글 스프레드시트 URL에서 데이터를 다운로드하여 pandas DataFrame으로 반환합니다.
    
    Parameters:
        sheet_url (str): 구글 스프레드시트 공유 URL
        sheet_name (str): 가져올 시트 이름 (기본값: None, 첫 번째 시트를 가져옴)
    
    Returns:
        pandas.DataFrame: 스프레드시트 데이터를 담은 DataFrame
    """
    try:
        # URL이 올바른 구글 스프레드시트 주소인지 확인
        if 'docs.google.com/spreadsheets' not in sheet_url:
            raise ValueError('올바른 구글 스프레드시트 URL이 아닙니다.')
            
        # URL에서 스프레드시트 ID 추출
        parsed_url = urlparse(sheet_url)
        if 'spreadsheets/d/' in sheet_url:
            sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
        else:
            query_params = parse_qs(parsed_url.query)
            sheet_id = query_params.get('id', [None])[0]
            
        if not sheet_id:
            raise ValueError('스프레드시트 ID를 찾을 수 없습니다.')
        
        # CSV 다운로드 URL 생성 (시트 이름 포함)
        csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        if sheet_name:
            csv_export_url += f'&gid={get_sheet_id(sheet_id, sheet_name)}'
        
        # 데이터 다운로드
        response = requests.get(csv_export_url)
        response.raise_for_status()  # HTTP 에러 체크
        
        # response의 인코딩을 UTF-8로 설정
        response.encoding = 'utf-8'
        
        # DataFrame으로 변환하여 반환 (encoding 파라미터 추가)
        return pd.read_csv(StringIO(response.text), encoding='utf-8')
        
    except requests.exceptions.RequestException as e:
        print(f'다운로드 중 오류가 발생했습니다: {e}')
    except ValueError as e:
        print(f'URL 처리 중 오류가 발생했습니다: {e}')
    except Exception as e:
        print(f'예상치 못한 오류가 발생했습니다: {e}')

def get_sheet_id(spreadsheet_id, sheet_name):
    """
    시트 이름으로부터 시트 ID(gid)를 가져옵니다.
    
    Parameters:
        spreadsheet_id (str): 스프레드시트 ID
        sheet_name (str): 시트 이름
    
    Returns:
        str: 시트 ID (gid)
    """
    try:
        # 스프레드시트 메타데이터 URL
        url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit/sheet?format=json'
        response = requests.get(url)
        response.raise_for_status()
        
        # JSON 응답에서 시트 정보 파싱
        sheet_data = response.json()
        for sheet in sheet_data.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        
        raise ValueError(f'시트 "{sheet_name}"를 찾을 수 없습니다.')
        
    except Exception as e:
        print(f'시트 ID를 가져오는 중 오류가 발생했습니다: {e}')
        return None
        
    
        
# 사용 예시
if __name__ == '__main__':
    sheet_url = '구글 스프레드시트 URL을 여기에 입력하세요'
    df = download_google_sheet(sheet_url, 'downloaded_data.csv')