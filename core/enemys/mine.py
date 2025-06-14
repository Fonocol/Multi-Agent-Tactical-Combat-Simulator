from core.entity import Entity
from core.utils import distance_to


class Mine(Entity):
    def __init__(self, x, y, trigger_radius=8.0, explosion_radius=3.0):
        super().__init__(x, y, radius=trigger_radius, etype="mine")
        self.explosion_radius = explosion_radius
        self.triggered = False

    def update(self, env):
        if self.triggered or not self.alive:
            return

        for agent in env.agents:
            if agent.alive and distance_to(self, agent) <= self.radius:
                self.triggered = True
                env.spawn_explosion(self.x, self.y, self.explosion_radius)
                self.alive = False
                agent.take_damage(50)
