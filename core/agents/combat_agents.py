import numpy as np
from .agent import Agent
from core.entity_types import EntityType

class ScoutAgent(Agent):
    def __init__(self, x, y, radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=90, fov_deg=120)
        self.speed = 2.0

    def decide_action(self, observation=None):
        vec = np.random.uniform(-1, 1, 2)
        vec /= np.linalg.norm(vec)
        vec *= self.speed

        self.facing_angle = np.arctan2(vec[1], vec[0])
        return {"type": "move", "dx": vec[0], "dy": vec[1]}
    
    def perform_action(self, action, env):

        """
        Exécute une action donnée par decide_action ou par une policy.
        """
        action_type = action["type"]

        if action_type == "move":
            dx, dy = action.get("dx", 0), action.get("dy", 0)
            vec = np.array([dx, dy], dtype=np.float64)
            norm = np.linalg.norm(vec)
            if norm != 0:
                vec /= norm
                self.facing_angle = np.arctan2(vec[1], vec[0])
            vec *= getattr(self, 'speed', 1.0)  # Fallback à 1.0 si pas d’attribut speed
            self.move(vec[0], vec[1], env)

        elif action_type == "wait":
            # L'agent ne fait rien ce tick
            pass

        elif action_type == "scan":
            # Étendre temporairement sa portée de vision
            original_range = self.range
            original_fov = self.fov
            self.effective_range = original_range * 1.5
            self.effective_fov = np.pi  # Vision à 180° temporairement
            # Le scan est pris en compte dans get_vision()


        elif action_type == "cloak":
            # Rend l’agent temporairement invisible
            self.cloaked = True
            self.cloak_duration = 5  # durée en ticks
            # Ajoute une logique ailleurs pour réduire cloak_duration à chaque tick

        elif action_type == "attack":
            #visible = self.get_vision(env.objects)
            #self.attack(visible)
            if self.energy >= 10:
                self.energy -= 10
                self.attack(env)

        else:
            # Action inconnue : l'ignorer ou raise une erreur
            pass
        
        self.update()


        # Autres types d’actions ici plus tard

        # D'autres types : "use_item", "scan", "defend", "wait"...


class SniperAgent(Agent):
    def __init__(self, x, y, radius=0.8,range_radius=100):
        super().__init__(x, y, radius=radius, range_radius=range_radius, fov_deg=90)
        self.attack_range = 10.0
        self.attack_power = 40

    def decide_action(self, observation=None):
        visible = observation or []
        targets = [o for o in visible if o.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE,EntityType.ENERGY_DRONE_ELITE,EntityType.ENEMY_TURREL]]
        return {"type": "attack"} if targets else super().decide_action()

    def attack(self,env):
        return super().attack(damage=self.attack_power,env=env)


class GuardAgent(Agent):
    def __init__(self, x, y, radius=0.8, guard_x=None, guard_y=None):
        super().__init__(x, y, radius=radius, range_radius=60, fov_deg=120)
        self.guard_position = np.array([guard_x or x, guard_y or y])
        self.patrol_radius = 25.0
        self.speed = 0.5

    def decide_action(self, observation=None):
        pos = np.array([self.x, self.y])
        dist = np.linalg.norm(pos - self.guard_position)

        if dist > self.patrol_radius:
            vec = self.guard_position - pos
        else:
            vec = np.random.uniform(-1, 1, 2)

        vec /= np.linalg.norm(vec)
        vec *= self.speed  # slow move
        self.facing_angle = np.arctan2(vec[1], vec[0])
        return {"type": "move", "dx": vec[0], "dy": vec[1]}

#Mission Kamikaze anti-tourelle  atteindre et detruire une tourelle il peu
# cacher invisible pour les tourelle par exemple une action qui le rend invisible au tourelle pour un tempd donner 
#a voir avec l'evolution par exemple le Decoy 
class KamikazeAgent(Agent):
    def __init__(self, x, y, radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=60, fov_deg=100)
        self.speed = 2.5
        self.explosion_range = 2.0
        self.explosion_damage = 100

    def decide_action(self, observation=None):
        visible = observation or []
        pos = np.array([self.x, self.y])
        targets = [o for o in visible if o.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE]]
        if targets:
            closest = min(targets, key=lambda o: np.linalg.norm(np.array([o.x, o.y]) - pos))
            vec = np.array([closest.x, closest.y]) - pos
            vec /= np.linalg.norm(vec)
            vec *= self.speed
            self.facing_angle = np.arctan2(vec[1], vec[0])
            return {"type": "move", "dx": vec[0], "dy": vec[1]}
        else:
            return super().decide_action()

    def perform_action(self, action, env):
        super().perform_action(action, env)
        pos = np.array([self.x, self.y])
        for obj in env.objects:
            if obj.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE] and obj.alive:
                if np.linalg.norm(np.array([obj.x, obj.y]) - pos) <= self.explosion_range:
                    obj.take_damage(self.explosion_damage)
                    self.health -= self.explosion_damage
                    print(f"[Kamikaze Agent] Explosion à ({self.x:.1f},{self.y:.1f}) !")


class SupportAgent(Agent):
    def __init__(self, x, y, radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=70, fov_deg=120)
        self.heal_range = 5.0
        self.heal_amount = 10

    def decide_action(self, observation=None):
        vec = np.random.uniform(-0.5, 0.5, 2)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm * 0.5
        self.facing_angle = np.arctan2(vec[1], vec[0])
        return {"type": "move", "dx": vec[0], "dy": vec[1]}

    def perform_action(self, action, env):
        super().perform_action(action, env)
        pos = np.array([self.x, self.y])
        for agent in env.agents:
            if agent != self and agent.alive:
                if np.linalg.norm(np.array([agent.x, agent.y]) - pos) <= self.heal_range:
                    agent.health = min(agent.health + self.heal_amount, 100)


class HeavyAgent(Agent):
    def __init__(self, x, y, radius=0.8):
        super().__init__(x, y, radius=radius, range_radius=40, fov_deg=90)
        self.health = 200
        self.speed = 0.6

    def decide_action(self, observation=None):
        vec = np.random.uniform(-1, 1, 2)
        vec /= np.linalg.norm(vec)
        vec *= self.speed
        self.facing_angle = np.arctan2(vec[1], vec[0])
        return {"type": "move", "dx": vec[0], "dy": vec[1]}
