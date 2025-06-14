import math
from .enemyBase import EnemyBase
from core.utils import distance_to


class EnemyKamikaze(EnemyBase):
    def __init__(self, x, y,radius=2.5, speed=0.2, explosion_radius=5.0, explosion_damage=50):
        super().__init__(x, y, radius=radius, health=50, speed=speed, etype="enemy_kamikaze")
        self.explosion_radius = explosion_radius
        self.explosion_damage = explosion_damage
        self.target = None

    def update(self, env):
        if not self.target or not self.target.alive:
            self.find_target(env)
        if self.target:
            self.move_towards_target()
            self.check_explosion(env)

    def find_target(self, env):
        self.target = None
        min_dist = float('inf')
        for agent in env.agents:
            if agent.alive:
                dist = distance_to(self, agent)
                if dist < min_dist:
                    min_dist = dist
                    self.target = agent

    def move_towards_target(self):
        if not self.target:
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        mag = math.hypot(dx, dy)
        if mag > 0:
            dx /= mag
            dy /= mag
            self.x += dx * self.speed
            self.y += dy * self.speed

    def check_explosion(self, env):
        if distance_to(self, self.target) <= self.explosion_radius:
            # Créer une explosion qui endommage tout dans radius
            env.spawn_explosion(self.x, self.y, self.explosion_radius)
            # Endommage tous les agents dans l’explosion
            for agent in env.agents:
                if distance_to(self, agent) <= self.explosion_radius:
                    agent.take_damage(self.explosion_damage)
            self.alive = False
