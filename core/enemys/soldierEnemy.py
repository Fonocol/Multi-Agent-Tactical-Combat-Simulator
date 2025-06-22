from core.entity import Entity
from core.utils import distance_to
import numpy as np


class SoldierEnemy(Entity):
    def __init__(self, x, y, radius=1.5, vision_range=15):
        super().__init__(x, y, radius)
        self.vision_range = vision_range
        self.speed = 1.0
        self.patrol_target = self._get_random_point()
        self.state = "patrol"  # patrol, chase, flee

    def _get_random_point(self):
        return np.random.uniform(0, 100, 2)

    def move_towards(self, target_pos):
        direction = target_pos - np.array([self.x, self.y])
        norm = np.linalg.norm(direction)
        if norm > 0:
            step = self.speed * direction / norm
            self.x += step[0]
            self.y += step[1]

    def move_away_from(self, targets):
        if not targets:
            return

        # Trouver l'ennemi le plus proche
        closest = min(targets, key=lambda t: distance_to(self, t))
        dx = self.x - closest.x
        dy = self.y - closest.y
        norm = np.linalg.norm([dx, dy])

        if norm > 0:
            self.x += self.speed * dx / norm
            self.y += self.speed * dy / norm


    def update(self, env):
        # Trouver agents visibles dans le rayon de vision
        visible_agents = [
            a for a in env.agents 
            if a.alive and distance_to(self, a) < self.vision_range
        ]

        # Chercher les alliés dans un rayon plus petit (10)
        allies = [
            a for a in env.objects
            if a.alive and isinstance(a, SoldierEnemy) and a is not self and distance_to(self, a) < 10
        ]

        if len(visible_agents) >= 2 and len(allies) == 0:
            
            self.state = "flee"
            self.move_away_from(visible_agents)
        elif visible_agents:
           
            self.state = "chase"
            closest = min(visible_agents, key=lambda a: distance_to(self, a))
            self.move_towards(np.array([closest.x, closest.y]))
            #attaquer
        else:
            
            self.state = "patrol"
            patrol_dist = np.linalg.norm(np.array([self.x, self.y]) - self.patrol_target)
            if patrol_dist < 1.0:
                self.patrol_target = self._get_random_point()
            self.move_towards(self.patrol_target)
