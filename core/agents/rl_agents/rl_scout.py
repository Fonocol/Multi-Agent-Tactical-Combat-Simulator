from core.agents.combat_agents import ScoutAgent

class RLScoutAgent(ScoutAgent):
    def __init__(self, x, y, radius=0.8):
        super().__init__(x, y, radius)
        self.external_action = None
        self.action_space = self._build_action_space()

    def _build_action_space(self):
        return [
            {"type": "move", "dx": 0, "dy": 0},
            {"type": "move", "dx": 1, "dy": 0},
            {"type": "move", "dx": -1, "dy": 0},
            {"type": "move", "dx": 0, "dy": 1},
            {"type": "move", "dx": 0, "dy": -1},
            {"type": "move", "dx": 1, "dy": 1},
            {"type": "move", "dx": -1, "dy": -1},
            {"type": "move", "dx": -1, "dy": 1},
            {"type": "move", "dx": 1, "dy": -1},
            {"type": "wait"},
            {"type": "scan"},
            {"type": "cloak"},
            {"type": "attack"},
            # {"type": "attack"} si le Scout peut se défendre
        ]


    def decide_action(self, observation=None):
        return self.external_action or self.action_space[0]


