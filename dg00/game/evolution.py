from datetime import datetime


class EvolutionSystem:
    def __init__(self, config):
        self.stages = config["stages"]
        
    def check_evolution(self, player_data):
        if player_data["stage"] == "디아블로몬":
            return None
            
        stage_config = self.stages[player_data["stage"]]
        current_count = player_data["count"]
        
        if current_count >= stage_config["evolution_count"]:
            if player_data["evolution_started"] is None:
                return {"status": "start_evolution"}
                
            evolution_time = datetime.fromisoformat(player_data["evolution_started"])
            time_passed = (datetime.now() - evolution_time).total_seconds()
            
            if time_passed >= stage_config["evolution_time"]:
                stages = list(self.stages.keys())
                current_index = stages.index(player_data["stage"])
                return {
                    "status": "evolved",
                    "new_stage": stages[current_index + 1]
                }
                
        return None