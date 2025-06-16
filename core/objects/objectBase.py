import math
import random
from core.entity import Entity


class ObjectBase(Entity):
    def __init__(self, x, y, radius=3.0, speed=0.1, etype="object",moving=False, ttl=15):
        super().__init__(x, y, radius, etype=etype)
        self.speed = speed
        self.alive = True
        self.moving =  moving
        self.ttl =ttl

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