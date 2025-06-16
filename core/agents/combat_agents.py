from .agent import Agent
from core.entity_types import EntityType
import math
import random

# | Classe          | Rôle principal                        | Style               |
# | --------------- | ------------------------------------- | ------------------- |
# | `ScoutAgent`    | Reconnaissance rapide + large vision  | Léger, rapide       |
# | `SniperAgent`   | Longue portée, attaque précise        | Lent, puissant      |
# | `GuardAgent`    | Défensif, reste proche d’un point/clé | Robuste, tank       |
# | `KamikazeAgent` | Charge, explose à l’impact            | Suicide, dégâts max |


class ScoutAgent(Agent):
    def __init__(self, x, y,radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=50, fov_deg=160)
        self.speed = 2.0

    def decide_action(self, observation=None):
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        norm = math.hypot(dx, dy)
        dx, dy = dx / norm * self.speed, dy / norm * self.speed

        self.facing_angle = math.atan2(dy, dx)
        return {"type": "move", "dx": dx, "dy": dy}


class SniperAgent(Agent):
    def __init__(self, x, y,radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=60, fov_deg=90)
        self.attack_range = 10.0
        self.attack_power = 40

    def decide_action(self, observation=None):
        visible = observation or []
        targets = [o for o in visible if o.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE]]
        if targets:
            return {"type": "attack"}
        else:
            return super().decide_action()

    def attack(self, objects):
        return super().attack(objects, damage=self.attack_power, attack_range=self.attack_range)


class GuardAgent(Agent):
    def __init__(self, x, y,radius=0.8, guard_x=None, guard_y=None):
        super().__init__(x, y, radius=radius, range_radius=35, fov_deg=120)
        self.guard_position = (guard_x or x, guard_y or y)
        self.patrol_radius = 25.0

    def decide_action(self, observation=None):
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        norm = math.hypot(dx, dy)
        dx, dy = dx / norm, dy / norm

        # Retourne vers la position à défendre s’il s’éloigne trop
        dist = math.hypot(self.x - self.guard_position[0], self.y - self.guard_position[1])
        if dist > self.patrol_radius:
            dx = self.guard_position[0] - self.x
            dy = self.guard_position[1] - self.y
            norm = math.hypot(dx, dy)
            dx, dy = dx / norm, dy / norm

        self.facing_angle = math.atan2(dy, dx)
        return {"type": "move", "dx": dx * 0.5, "dy": dy * 0.5}  # lent


class KamikazeAgent(Agent):
    def __init__(self, x, y,radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=25, fov_deg=100)
        self.speed = 2.5
        self.explosion_range = 2.0
        self.explosion_damage = 100

    def decide_action(self, observation=None):
        visible = observation or []
        targets = [o for o in visible if o.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE]]
        if targets:
            # Fonce vers la cible la plus proche
            closest = min(targets, key=lambda o: math.hypot(o.x - self.x, o.y - self.y))
            dx = closest.x - self.x
            dy = closest.y - self.y
            norm = math.hypot(dx, dy)
            dx, dy = dx / norm * self.speed, dy / norm * self.speed
            self.facing_angle = math.atan2(dy, dx)
            return {"type": "move", "dx": dx, "dy": dy}
        else:
            return super().decide_action()

    def perform_action(self, action, env):
        super().perform_action(action, env)
        # Explose si ennemi proche
        for obj in env.objects:
            if obj.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE] and obj.alive:
                dist = math.hypot(obj.x - self.x, obj.y - self.y)
                if dist <= self.explosion_range:
                    obj.take_damage(self.explosion_damage)
                    self.health -= self.explosion_damage
                    #self.alive = False
                    print(f"[Kamikaze Agent] Explosion à ({self.x:.1f},{self.y:.1f}) !")


class SupportAgent(Agent):
    def __init__(self, x, y,radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=35, fov_deg=120)
        self.heal_range = 5.0
        self.heal_amount = 10

    def decide_action(self, observation=None):
        # Se déplace peu, priorise le soin
        dx, dy = random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)
        norm = math.hypot(dx, dy)
        if norm > 0:
            dx, dy = dx / norm * 0.5, dy / norm * 0.5
        self.facing_angle = math.atan2(dy, dx)
        return {"type": "move", "dx": dx, "dy": dy}

    def perform_action(self, action, env):
        super().perform_action(action, env)
        # Soigne les agents proches
        for agent in env.agents:
            if agent != self and agent.alive:
                dist = math.hypot(agent.x - self.x, agent.y - self.y)
                if dist <= self.heal_range:
                    agent.health = min(agent.health + self.heal_amount, 100)


class HeavyAgent(Agent):
    def __init__(self, x, y,radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=25, fov_deg=90)
        self.health = 200
        self.speed = 0.6

    def decide_action(self, observation=None):
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        norm = math.hypot(dx, dy)
        dx, dy = dx / norm * self.speed, dy / norm * self.speed
        self.facing_angle = math.atan2(dy, dx)
        return {"type": "move", "dx": dx, "dy": dy}
