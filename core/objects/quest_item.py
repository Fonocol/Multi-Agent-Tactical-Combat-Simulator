from core.entity import Entity
from core.utils import distance_to

class ObjectiveItem(Entity):
    def __init__(self, x, y, radius=2.0, reward=20):
        super().__init__(x, y, radius, etype="target")
        self.collected = False
        self.reward = reward

    def update(self, env):
        for agent in env.agents:
            if not self.collected and agent.alive:
                
                dist = distance_to(self,agent) 
                if dist <= self.radius + agent.radius:
                    self.collected = True
                    self.alive = False
                    agent.energy += self.reward  # ou agent.score += self.reward
                    # Tu peux aussi faire : env.log_quest_collected(agent, self)
