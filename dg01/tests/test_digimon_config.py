from dg01.digimon_config import (
    DFP_STAGE_CONFIG, 
    STAGE_CONFIG,
    STAGES,
    get_stage_config,
    get_battle_chance,
    get_random_message,
    get_evolution_quiz
)


def test_stage_config():
    """
    ['stage_name', 'stage_idx', 'evolution_time', 'evolution_count',
       'copy_rate', 'data_rate', 'description', 'image_path', 'battle_chance',
       'random_messages', 'evolution_quiz', 'special_move']
    """
    stage_idx = 0
    print(f"{get_stage_config(stage_idx)=}")
    print(f"{get_battle_chance(stage_idx)=}")
    print(f"{get_random_message(stage_idx)=}")
    print(f"{get_evolution_quiz(stage_idx)=}")

    print(f"=== {sorted(STAGES.keys())[0]} ===")

    
