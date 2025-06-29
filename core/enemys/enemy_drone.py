import numpy as np
from core.entity_types import EntityType, Role
from .enemyBase import EnemyBase
from core.utils import MAX_DRONES, distance_to
import math
import random

class EnemyDrone(EnemyBase):  
    def __init__(self, x, y, patrol_radius=10, radius=3.0,fire_range = 10.0 ,patrol_type="circle",role:str='any'):
        super().__init__(x, y, radius=radius, health=100, speed=0.1, etype=EntityType.ENERGY_DRONE)
        self.patrol_radius = patrol_radius
        self.center = (x, y)
        self.angle = 0.0
        self.attack_range = 15.0
        self.fire_range = fire_range
        self.target = None
        self.patrol_type = patrol_type.lower()
        self.random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.random_timer = 0
        
        self.last_reproduction_time = 0
        self.reproduction_cooldown = 50  # ticks minimum entre deux repros
        self.health_cost = 20
        
        self.cooldown = 5
        self.cooldown_timer = 0
        
        self.role = role.lower()

    def update(self, env):
        self.last_reproduction_time += 1
        self.find_target(env)
        if self.target:
            self.chase_or_attack(env)
        else:
            self.patrol()
            
        self._maybe_reproduce(env)

    def find_target(self, env):
        self.target = None
        for agent in env.agents:
            if agent.alive and distance_to(self, agent) <= self.attack_range:
                self.target = agent
                break

    def chase_or_attack(self, env):
        if not self.target or not self.target.alive:
            return
        
        dist = distance_to(self, self.target)
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        mag = math.hypot(dx, dy)
        
        if mag > 0:
            dx /= mag
            dy /= mag
            
        if dist > self.fire_range:
            self.x += dx * self.speed * 2
            self.y += dy * self.speed * 2
        else:
            # Attack
            self.cooldown_timer +=1
            if  self.cooldown_timer >= self.cooldown:
                noisex,noisey = np.random.randint(-5,5),np.random.randint(-5,5)
                if self.role == Role.JammerComunication:
                    env.spawn_jammer_communication(self.x+noisex, self.y+noisey,moving=True,owner=self)
                elif self.role == Role.SMOKER:
                    env.spawn_smoke_zone(self.x+noisex, self.y+noisey,moving=True, owner=self)
                    
                else:
                    env.spawn_projectile(self.x, self.y, dx, dy, self)
                
                self.cooldown_timer =0
    
    
            
    def patrol(self):
        self.angle += self.speed
        
        if self.patrol_type == "circle":
            # Mouvement circulaire classique
            self.x = self.center[0] + self.patrol_radius * math.cos(self.angle)
            self.y = self.center[1] + self.patrol_radius * math.sin(self.angle)

        elif self.patrol_type == "ellipse":
            # Ellipse avec grand axe horizontal
            a = self.patrol_radius
            b = self.patrol_radius * 0.6  
            self.x = self.center[0] + a * math.cos(self.angle)
            self.y = self.center[1] + b * math.sin(self.angle)

        elif self.patrol_type == "lemniscate":
            # Lemniscate de Bernoulli (∞)
            a = self.patrol_radius
            scale = 0.5 
            t = self.angle * 2 
            
            denom = 1 + math.sin(t)**2
            r = (a * math.sqrt(2) * math.cos(t)) / denom
            self.x = self.center[0] + r * math.cos(t) * scale
            self.y = self.center[1] + r * math.sin(t) * scale

        elif self.patrol_type == "spiral":
            # Spirale qui s'éloigne progressivement
            r = self.patrol_radius * (1 + 0.05 * (self.angle % (2*math.pi)))
            self.x = self.center[0] + r * math.cos(self.angle)
            self.y = self.center[1] + r * math.sin(self.angle)

        elif self.patrol_type == "random":
            # Mouvement aléatoire 
            self.random_timer += 1
            if self.random_timer > 60:  
                self.random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
                self.random_timer = 0
                
            self.x += self.random_direction[0] * self.speed
            self.y += self.random_direction[1] * self.speed
            
            # Garde le drone près de son point central
            dist_to_center = math.hypot(self.x - self.center[0], self.y - self.center[1])
            if dist_to_center > self.patrol_radius * 1.5:
                self.random_direction = (
                    (self.center[0] - self.x) / dist_to_center,
                    (self.center[1] - self.y) / dist_to_center
                )
                
        elif self.patrol_type == "square":
            # Définir les coins du carré
            half_size = self.patrol_radius
            corners = [
                (self.center[0] - half_size, self.center[1] - half_size),  # Coin inférieur gauche
                (self.center[0] + half_size, self.center[1] - half_size),  # Coin inférieur droit
                (self.center[0] + half_size, self.center[1] + half_size),  # Coin supérieur droit
                (self.center[0] - half_size, self.center[1] + half_size)   # Coin supérieur gauche
            ]
            
            # Durée pour atteindre chaque coin (en radians)
            corner_duration = math.pi/2  # 90° de rotation par côté
            
            # Calculer l'index du coin actuel et le progrès vers le prochain coin
            current_corner_idx = int(self.angle // corner_duration) % 4
            next_corner_idx = (current_corner_idx + 1) % 4
            progress = (self.angle % corner_duration) / corner_duration
            
            # Interpolation linéaire entre les coins
            start_x, start_y = corners[current_corner_idx]
            end_x, end_y = corners[next_corner_idx]
            self.x = start_x + (end_x - start_x) * progress
            self.y = start_y + (end_y - start_y) * progress
            
            # Avancer l'angle plus lentement pour un mouvement plus naturel
            self.angle += self.speed * 0.5
            
        elif self.patrol_type == "square_random":
            half_size = self.patrol_radius
            if not hasattr(self, 'square_target'):
                # Choisir un point aléatoire dans le carré
                self.square_target = (
                    self.center[0] + random.uniform(-half_size, half_size),
                    self.center[1] + random.uniform(-half_size, half_size)
                )
            
            # Se déplacer vers la cible
            dx = self.square_target[0] - self.x
            dy = self.square_target[1] - self.y
            dist = math.hypot(dx, dy)
            
            if dist < self.speed * 2:  # Si proche de la cible, en choisir une nouvelle
                self.square_target = (
                    self.center[0] + random.uniform(-half_size, half_size),
                    self.center[1] + random.uniform(-half_size, half_size)
                )
            elif dist > 0:
                # Normaliser la direction
                dx /= dist
                dy /= dist
                self.x += dx * self.speed
                self.y += dy * self.speed
            
            # Garantir qu'on reste dans les limites
            self.x = max(self.center[0] - half_size, min(self.center[0] + half_size, self.x))
            self.y = max(self.center[1] - half_size, min(self.center[1] + half_size, self.y))

        else:  # Default to circle
            self.x = self.center[0] + self.patrol_radius * math.cos(self.angle)
            self.y = self.center[1] + self.patrol_radius * math.sin(self.angle)

    def _maybe_reproduce(self, env):
            num_drones = sum(1 for e in env.objects if isinstance(e, EnemyDrone))
            if num_drones >= MAX_DRONES:
                return

            if self.last_reproduction_time < self.reproduction_cooldown:
                return

            # Pas assez de santé
            if self.health < self.health_cost + 10:
                return

            # Probabilité dynamique
            repro_chance = max(0.001, 0.01 * (1 - num_drones / MAX_DRONES))
            if random.random() < repro_chance:
                self._reproduce(env)
                
                self.last_reproduction_time = 0
                self.health -= self.health_cost
                if self.health <= 0:
                    self.alive = False

    def _reproduce(self, env):
        child = EnemyDrone(
            x=self.x + random.uniform(-2, 2),
            y=self.y + random.uniform(-2, 2),
            patrol_radius=self.patrol_radius,
            radius=self.radius,
            fire_range=self.fire_range,
            patrol_type=random.choice(["circle", "lemniscate", "random", "square"]),
            role=self.role,
        )
        env.spawn_entity(child)