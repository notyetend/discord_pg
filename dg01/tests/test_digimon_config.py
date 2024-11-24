from dg01.games.digimon.digimon_config import (
    DFP_STAGE_CONFIG, 
    get_next_stage,
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
    stage_name = "츠메몬"
    print(f"{get_next_stage(stage_name)=}")
    print(f"{get_stage_config(stage_name)=}")
    print(f"{get_battle_chance(stage_name)=}")
    print(f"{get_random_message(stage_name)=}")
    print(f"{get_evolution_quiz(stage_name)=}")

    
