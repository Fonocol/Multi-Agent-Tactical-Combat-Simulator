import math
from .enemyBase import EnemyBase
from core.utils import distance_to


class EnemyTurret(EnemyBase):
    def __init__(self, x, y, radius=2.0, health=150, fire_range=20):
        super().__init__(x, y, radius=radius, health=health, speed=0, etype="enemy_turret")
        self.fire_range = fire_range
        self.cooldown_timer = 0
        self.target = None

        # Health system
        self.health_max = 150
        self.cooldown_min = 5
        self.cooldown_max = 15
        self.last_health = self.health
        self.update_cooldown()

        # FOV and vision
        self.facing_angle = 0  # Radians
        self.fov = math.radians(90)  # 90 degree cone of vision
        self.rotation_speed = math.radians(5)  # Rotation per update when idle
        self.scan_mode = True  # If True, rotate to search for target

    def update(self, env):
        if self.health != self.last_health:
            self.update_cooldown()
            self.last_health = self.health

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

        if self.scan_mode:
            self.facing_angle = (self.facing_angle + self.rotation_speed) % (2 * math.pi)

        self.find_target(env)
        if self.target and self.cooldown_timer <= 0:
            self.shoot(env)

    def find_target(self, env):
        self.target = None
        for agent in env.agents:
            if not agent.alive:
                continue
            if distance_to(self, agent) > self.fire_range:
                continue
            if distance_to(self, agent) <= self.radius:
                env.spawn_jammer(self.x, self.y, True, self)

            dx, dy = agent.x - self.x, agent.y - self.y
            angle_to_agent = math.atan2(dy, dx)
            angle_diff = (angle_to_agent - self.facing_angle + math.pi) % (2 * math.pi) - math.pi

            if abs(angle_diff) <= self.fov / 2:
                self.target = agent
                self.scan_mode = False
                return

        self.scan_mode = True  # No target found, resume scanning

    def shoot(self, env):
        if not self.target or not self.target.alive:
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        mag = math.hypot(dx, dy)
        if mag > 0:
            dx /= mag
            dy /= mag
            self.facing_angle = math.atan2(dy, dx)  # Face toward the target

        env.spawn_projectile(self.x, self.y, dx, dy, self)
        self.cooldown_timer = self.cooldown

    def update_cooldown(self):
        ratio = self.health / self.health_max
        self.cooldown = self.cooldown_max - (ratio * (self.cooldown_max - self.cooldown_min))

    def to_dict(self):
        data = super().to_dict()
        data["cooldown_timer"] = self.cooldown_timer
        data["facing_angle"] = self.facing_angle
        data["fov"] = self.fov
        return data
