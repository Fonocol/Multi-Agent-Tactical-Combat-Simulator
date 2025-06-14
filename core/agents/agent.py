import math
import random
from core.entity import Entity
from core.entity_types import EntityType
from core.utils import is_blocked_by_wall


class Agent(Entity):
    def __init__(self, x, y, radius=1.0,range_radius=30,fov_deg=90):
        super().__init__(x, y, radius, etype="agent")
        self.energy = 100
        self.health = 100
        self.facing_angle = 0.0
        self.range = range_radius
        self.fov = math.radians(fov_deg)
        
        self.effective_range = self.range
        self.effective_fov = self.fov
        self.inbox = []

    def decide_action(self, observation=None):
        """
        Pour l'instant : action aléatoire.
        Plus tard : pourra utiliser observation + policy RL
        """
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)

        
        if dx != 0 or dy != 0:
            norm = math.sqrt(dx ** 2 + dy ** 2)
            dx /= norm
            dy /= norm
            self.facing_angle = math.atan2(dy, dx)

        return {"type": "move", "dx": dx, "dy": dy}
    
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
    
    def get_orientation(self):
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.facing_angle,
            'length':self.effective_range,
            'fov':self.effective_fov
        }
        
    def to_dict(self):
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
        new_x = self.x + dx
        new_y = self.y + dy

        if env:
            for obj in env.objects:
                if getattr(obj, "block_movement", False):
                    # Collision test
                    if ((obj.x - new_x)**2 + (obj.y - new_y)**2)**0.5 <= self.radius + obj.radius+0.5:
                        return  
        self.x = new_x
        self.y = new_y
        
        if self.x <0 or self.x>500 or self.y <0 or self.y>500:
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
        
        for obj in objects:
            if not obj.alive:
                continue

            dx = obj.x - self.x
            dy = obj.y - self.y
            dist = math.hypot(dx, dy)
            
            if obj.etype == EntityType.WALL:
                walls.append(obj)

            if obj.etype == EntityType.SMOKE and dist <= obj.radius:
                self.effective_range *= obj.get_vision_penalty()
            
            if obj.etype == EntityType.JAMMER and dist <= obj.radius:
                # Vision bloquée complètement
                return [obj]
            
        
        # Calcul de la vision normale
        for obj in objects:
            if not obj.alive or obj == self:
                continue

            dx = obj.x - self.x
            dy = obj.y - self.y
            dist = math.hypot(dx, dy)

            if dist > self.effective_range:
                continue
            if is_blocked_by_wall(self, obj, walls):
                continue  # objet caché par un mur

            direction = math.atan2(dy, dx)
            delta = self._angle_diff(direction, self.facing_angle)

            if abs(delta) <= self.effective_fov / 2:
                vision.append(obj)

        return vision
    

    def _angle_diff(self, a, b):
        diff = a - b
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        return diff
    

    
    def attack(self, objects, damage=20, attack_range=3.0):
        for obj in objects:
            if obj.etype in [EntityType.ENERGY_DRONE,EntityType.ENERGY_KAMIKAZE] and obj.alive:
                dist = math.hypot(obj.x - self.x, obj.y - self.y)
                if dist <= attack_range:
                    obj.take_damage(damage)
                    print(f"[Agent @({self.x:.1f},{self.y:.1f})] a attaqué un ennemi @({obj.x:.1f},{obj.y:.1f})")
                    return True
        return False
    
    
    def send_message(self):
        """Exemple de message si un ennemi est repéré dans la vision"""
        messages = []
        visible_objects = self.get_vision(self.env.objects) if hasattr(self, 'env') else []

        for obj in visible_objects:
            if obj.etype in ["enemy", EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE]:
                messages.append({
                    "type": "enemy_spotted",
                    "pos": (obj.x, obj.y),
                    "sender": id(self)
                })
        return messages 

    def receive_messages(self, messages):
        """Stocke les messages utiles dans l'inbox"""
        self.inbox = []

        for msg in messages:
            if msg["sender"] == id(self):
                continue  # ne pas recevoir ses propres messages
            if self._distance(msg["pos"], (self.x, self.y)) <= self.range:
                self.inbox.append(msg)

    def _distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

