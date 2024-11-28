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