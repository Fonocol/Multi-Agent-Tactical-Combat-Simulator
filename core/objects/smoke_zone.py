import math
import random
from core.entity import Entity
from core.entity_types import EntityType

class SmokeZone(Entity):
    def __init__(self, x, y, radius=5.0,moving=False, ttl=15, speed=1.5):
        super().__init__(x, y, radius, etype="smoke",moving=moving)
        self.vision_penalty = 0.8  # Réduit la range de vision à 80%
        self.ttl = ttl
        self.speed = speed
        
    def get_vision_penalty(self):
        return self.vision_penalty
    
    def update(self, env=None):
        if not self.alive :
            return
        if not self.moving:
            return
        
        self.ttl -= 1
        if self.ttl <= 0:
            self.alive = False
            return

        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        norm = math.hypot(dx, dy)
        self.x += (dx / norm) * self.speed
        self.y += (dy / norm) * self.speed
    

#bloc la vision
class JammerZone(Entity):  
    def __init__(self, x, y, radius=6.0,moving=False, ttl=15, speed=1.5):
        super().__init__(x, y, radius, etype="jammer",moving=moving)
        self.block_vision = True
        self.ttl = ttl
        self.speed = speed

    def update(self, env=None):
        if not self.alive :
            return
        if not self.moving:
            return
        
        self.ttl -= 1
        if self.ttl <= 0:
            self.alive = False
            return

        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        norm = math.hypot(dx, dy)
        self.x += (dx / norm) * self.speed
        self.y += (dy / norm) * self.speed
    
        
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




