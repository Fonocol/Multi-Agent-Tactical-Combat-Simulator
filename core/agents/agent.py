from typing import Any, Dict
import numpy as np
from core.entity import Entity
from core.entity_types import EntityType
from core.utils import is_blocked_by_wall


class Agent(Entity):
    def __init__(self, x:float, y:float, radius:float=1.0,range_radius:float=30,fov_deg:float=90):
        super().__init__(x, y, radius, etype="agent")
        self.energy = 100
        self.health = 100
        self.facing_angle = 0.0
        self.range = range_radius
        self.fov = np.deg2rad(fov_deg)
        
        self.effective_range = self.range
        self.effective_fov = self.fov
        self.can_communicate = True
        self.inbox = []

    def decide_action(self, observation=None):
        """
        Pour l'instant : action aléatoire.
        Plus tard : pourra utiliser observation + policy RL
        """
        vec = np.random.uniform(-1, 1, size=2)
        norm = np.linalg.norm(vec)

        if norm > 0:
            vec = vec / norm
            self.facing_angle = np.arctan2(vec[1], vec[0])

        return {"type": "move", "dx": vec[0], "dy": vec[1]}

    
    
    def perform_action(self, action, env):
        """
        Exécute une action donnée par decide_action ou par une policy.
        """
        if action["type"] == "move":
            self.move(action["dx"], action["dy"], env)

        elif action["type"] == "attack":
            visible = self.get_vision(env.objects)
            self.attack(visible)

        # D'autres types : "use_item", "scan", "defend", "wait"...
    
    def get_orientation(self)-> Dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.facing_angle,
            'length':self.effective_range,
            'fov':self.effective_fov
        }
        
    def to_dict(self)-> Dict[str, Any]:
        return {
                'x': self.x,
                'y': self.y,
                'type': 'agent',
                'health': self.health,
                'energy': self.energy,
                'range':self.range,
                'radius':self.radius
    }

    
    
    def move(self, dx, dy, env=None):
        new_pos = np.array([self.x + dx, self.y + dy])

        if env:
            for obj in env.objects:
                if getattr(obj, "block_movement", False):
                    dist = np.linalg.norm([obj.x - new_pos[0], obj.y - new_pos[1]])
                    if dist <= self.radius + obj.radius + 0.5:
                        return

        self.x, self.y = new_pos

        if not (0 <= self.x <= 500 and 0 <= self.y <= 500):
            self.health = 0
            self.alive = False

    
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            

    def get_vision(self, objects):
        vision = []
        self.effective_range = self.range
        self.effective_fov = self.fov
        walls = []
        vec_self = np.array([self.x, self.y])
        
        for obj in objects:
            if not obj.alive:
                continue

            vec_obj = np.array([obj.x, obj.y])
            vec = vec_obj - vec_self
            dist = np.linalg.norm(vec)
            
            if obj.etype == EntityType.WALL:
                walls.append(obj)

            if obj.etype == EntityType.SMOKE and dist <= obj.radius:
                self.effective_range *= obj.get_vision_penalty()

            if obj.etype == EntityType.JAMMER and dist <= obj.radius:
                return [obj]  # Vision bloquée

        # Deuxième passe : vision normale
        for obj in objects:
            if not obj.alive or obj == self:
                continue

            vec_obj = np.array([obj.x, obj.y])
            vec = vec_obj - vec_self
            dist = np.linalg.norm(vec)

            if dist > self.effective_range:
                continue
            if is_blocked_by_wall(self, obj, walls):
                continue

            direction = np.arctan2(vec[1], vec[0])
            delta = self._angle_diff(direction, self.facing_angle)

            if abs(delta) <= self.effective_fov / 2:
                vision.append(obj)

        return vision
  

    def _angle_diff(self, a, b):
        diff = (a - b + np.pi) % (2 * np.pi) - np.pi
        return diff

    
    def attack(self, objects, damage=20, attack_range=3.0):
        self_pos = np.array([self.x, self.y])
        for obj in objects:
            if obj.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE] and obj.alive:
                dist = np.linalg.norm(self_pos - np.array([obj.x, obj.y]))
                if dist <= attack_range:
                    obj.take_damage(damage)
                    print(f"[Agent @({self.x:.1f},{self.y:.1f})] a attaqué un ennemi @({obj.x:.1f},{obj.y:.1f})")
                    return True
        return False

    
    
    def send_message(self):
        if not self.can_communicate:
            return []

        if self.is_jammed(self.env.objects):
            print(f"Agent @({self.x:.1f},{self.y:.1f}) est brouillé !")
            return []  # Communication bloquée
    

        messages = []
        visible_objects = self.get_vision(self.env.objects) if hasattr(self, 'env') else []
        for obj in visible_objects:
            if obj.etype in ["enemy", EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE]:
                messages.append({
                    "type": "enemy_spotted",
                    "pos": (obj.x, obj.y),
                    "sender": self.id
                })
        return messages

    def receive_messages(self, messages):
        if not self.can_communicate or self.is_jammed(self.env.objects):
            self.inbox = []
            return
        


        self.inbox = [msg for msg in messages
                    if msg["sender"] != self.id and self._distance(msg["pos"], (self.x, self.y)) <= self.range]

    
    def is_jammed(self, objects):
        for obj in objects:
            if obj.etype == EntityType.JammerComunication:
                if self._distance((self.x, self.y), (obj.x, obj.y)) <= obj.radius:
                    return True
        return False


    def _distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

