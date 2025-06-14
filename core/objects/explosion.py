from core.entity import Entity
from core.utils import distance_to


class Explosion(Entity):
    def __init__(self, x, y, radius=5.0, duration=10):
        super().__init__(x, y, radius=radius, etype="explosion")
        self.timer = duration

    def update(self, env):
        if not self.alive:
            return

        for agent in env.agents:
            if agent.alive and distance_to(self, agent) <= self.radius:
                agent.take_damage(20)

        self.timer -= 1
        if self.timer <= 0:
            self.alive = False
