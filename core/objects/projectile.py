from core.entity import Entity
from core.entity_types import EntityType
from core.utils import distance_to


class Projectile(Entity):
    def __init__(self, x, y, dx, dy, owner=None, speed=1.5, radius=1.5, damage=15):
        super().__init__(x, y, radius, etype="projectile")
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.alive = True
        self.ttl = 40  # Durée de vie max (steps)

    def update(self, env):
        if not self.alive:
            return

        self.ttl -= 1
        if self.ttl <= 0:
            self.alive = False
            return

        # Avancer le projectile
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        # === 1. Collision avec AGENTS ===
        for agent in env.agents:
            if agent is self.owner:
                continue  # Ne pas toucher le tireur
            if agent.alive and distance_to(self, agent) <= (self.radius + agent.radius):
                if getattr(self.owner, "etype", None) in [EntityType.ENEMY, EntityType.ENERGY_DRONE,EntityType.ENERGY_DRONE_ELITE, EntityType.ENERGY_KAMIKAZE,EntityType.ENEMY_TURREL]:
                    agent.take_damage(self.damage)
                    self.alive = False
                    return

        # === 2. Collision avec ENNEMIS ===
        for obj in env.objects:
            if obj is self or not hasattr(obj, "alive") or not obj.alive:
                continue

            if obj.etype in [EntityType.ENEMY,EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE, EntityType.ENERGY_DRONE_ELITE,EntityType.ENEMY_TURREL]:
                if getattr(self.owner, "etype", None) == EntityType.AGENT:
                    if distance_to(self, obj) <= (self.radius + obj.radius):
                        obj.take_damage(self.damage)
                        self.owner.last_attack_success = True 
                        self.alive = False
                        return

        # === 3. Collision avec OBJETS SPÉCIAUX ===
        for obj in env.objects:
            if obj is self or not hasattr(obj, "alive") or not obj.alive:
                continue

            if obj.etype in [EntityType.WALL, EntityType.AGENT, EntityType.DECOY]:
                if distance_to(self, obj) <= (self.radius + obj.radius):
                    self.alive = False
                    return


