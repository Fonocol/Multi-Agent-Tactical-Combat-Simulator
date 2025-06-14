from core.entity import Entity
from core.entity_types import EntityType
from core.utils import distance_to


class Projectile(Entity):
    def __init__(self, x, y, dx, dy, owner=None, speed=1.5, radius=2, damage=10):
        super().__init__(x, y, radius, etype="projectile")
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.alive = True
        self.ttl = 20  # Durée de vie max (steps)

    def update(self, env):
        if not self.alive:
            return

        self.ttl -= 1
        if self.ttl <= 0:
            self.alive = False
            return

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # Collision avec agents
        for agent in env.agents:
            if agent is self.owner:
                continue
            if agent.alive and distance_to(self, agent) <= (self.radius + agent.radius):
                agent.take_damage(self.damage)
                self.alive = False
                return

        # Collision avec objets (ex: murs, ennemis ?)
        for obj in env.objects:
            if obj is self or obj.etype in [EntityType.PROJECTILE, EntityType.ENEMY]:
                continue
            if hasattr(obj, "alive") and not obj.alive:
                continue
            
            if obj.etype in [EntityType.AGENT,EntityType.WALL]:
                if distance_to(self, obj) <= (self.radius + obj.radius):
                    self.alive = False
                    return
