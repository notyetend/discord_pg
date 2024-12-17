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
            