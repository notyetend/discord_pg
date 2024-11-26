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