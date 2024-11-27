import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from dg01.digimon_config import STAGES, STAGE_CONFIG, get_next_stage_idx
from dg01.digimon_logic import DigimonLogic

class MockDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls._mock_now

    @classmethod
    def set_now(cls, dt):
        cls._mock_now = dt

@pytest.fixture
def digimon_logic():
    return DigimonLogic()

@pytest.fixture
def mock_now():
    return datetime(2024, 1, 1, tzinfo=timezone.utc)

@pytest.fixture
def base_player_data():
    return {
        "stage_idx": 0,
        "count": 0,
        "evolution_started": None
    }

@pytest.mark.parametrize(
    "stage_idx",
    [idx for idx in STAGES.keys() if idx != max(STAGES.keys())]  # 마지막 stage 제외
)
def test_check_evolution_stages(digimon_logic, base_player_data, mock_now, stage_idx):
    """각 stage의 진화 과정 테스트"""
    with patch('dg01.digimon_logic.datetime', MockDateTime):
        MockDateTime.set_now(mock_now)
        base_player_data["stage_idx"] = stage_idx
        evolution_time = STAGE_CONFIG[stage_idx]["evolution_time"]
        required_count = STAGE_CONFIG[stage_idx]["evolution_count"]
        next_stage_idx = get_next_stage_idx(stage_idx)
        
        # 1. count가 부족한 경우
        base_player_data["count"] = required_count - 1
        result = digimon_logic.check_evolution(base_player_data)
        assert result is None

        # 2. 진화 조건 충족 시 진화 시작
        base_player_data["count"] = required_count
        result = digimon_logic.check_evolution(base_player_data)
        assert result is not None
        assert "evolution_started" in result
        assert result["evolution_started"] == mock_now.isoformat()

        # 3. 진화 중간 과정 체크
        base_player_data["evolution_started"] = mock_now.isoformat()
        if evolution_time > 0:  # 디지타마(stage 0)는 진화 시간이 0
            MockDateTime.set_now(mock_now + timedelta(seconds=evolution_time - 1))
            result = digimon_logic.check_evolution(base_player_data)
            assert result is None

        # 4. 진화 완료 체크
        MockDateTime.set_now(mock_now + timedelta(seconds=evolution_time))
        result = digimon_logic.check_evolution(base_player_data)
        assert result is not None
        assert result["status"] == "evolved"
        assert result["new_stage_idx"] == next_stage_idx

def test_stage_index_consistency():
    """stage 관련 설정의 일관성 검사"""
    # STAGES와 STAGE_CONFIG의 일관성 체크
    assert len(STAGES) == len(STAGE_CONFIG), "STAGES와 STAGE_CONFIG의 길이가 일치하지 않습니다"
    
    # 각 stage_idx가 양쪽 설정에 모두 존재하는지 체크
    for idx in STAGES.keys():
        assert STAGE_CONFIG[idx]["stage_idx"] == idx, f"stage_idx {idx}의 설정이 일치하지 않습니다"

def test_check_evolution_final_stage(digimon_logic, base_player_data, mock_now):
    """최종 stage 테스트"""
    with patch('dg01.digimon_logic.datetime', MockDateTime):
        MockDateTime.set_now(mock_now)
        final_stage = max(STAGES.keys())
        base_player_data["stage_idx"] = final_stage
        base_player_data["count"] = 999999999
        
        result = digimon_logic.check_evolution(base_player_data)
        assert result is None