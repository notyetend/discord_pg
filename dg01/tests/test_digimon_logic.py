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