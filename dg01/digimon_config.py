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