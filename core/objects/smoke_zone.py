import math
import random
from core.entity import Entity
from core.entity_types import EntityType

class SmokeZone(Entity):
    def __init__(self, x, y, radius=5.0):
        super().__init__(x, y, radius, etype="smoke")
        self.vision_penalty = 0.8  # Réduit la range de vision à 80%
        
    def get_vision_penalty(self):
        return self.vision_penalty

#bloc la vision
class JammerZone(Entity):  
    def __init__(self, x, y, radius=6.0):
        super().__init__(x, y, radius, etype="jammer")
        self.block_vision = True
        
class JammerCommunication(Entity):
    def __init__(self, x, y, radius=20.0, speed=1.5, ttl=15):
        super().__init__(x, y, radius, etype=EntityType.JammerComunication)
        self.speed = speed
        self.ttl = ttl
        self.alive = True

    def update(self, env=None):
        if not self.alive:
            return

        self.ttl -= 1
        if self.ttl <= 0:
            self.alive = False
            return

        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        norm = math.hypot(dx, dy)
        self.x += (dx / norm) * self.speed
        self.y += (dy / norm) * self.speed




