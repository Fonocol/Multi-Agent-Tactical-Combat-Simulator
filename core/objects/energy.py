from core.entity import Entity
from core.utils import distance_to


class EnergySource(Entity):
    def __init__(self, x, y, radius=1.0, energy=30):
        super().__init__(x, y, radius=radius, etype="energy")
        self.energy = energy

    def update(self, env):
        for agent in env.agents:
            if agent.alive and distance_to(self, agent) <= self.radius:
                agent.energy += self.energy
                self.alive = False
                break
