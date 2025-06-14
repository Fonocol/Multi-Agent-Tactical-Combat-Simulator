from core.entity import Entity
from core.utils import distance_to

class RockWall(Entity):
    def __init__(self, x, y, radius=2.0):
        super().__init__(x, y, radius, etype="wall")
        self.block_movement = True
        self.block_vision = True  # utilisé pour couper la vision

    def blocks(self, agent):
        # Collision simple (cercle)
        dist = distance_to(self,agent) 
        return dist <= self.radius + agent.radius
