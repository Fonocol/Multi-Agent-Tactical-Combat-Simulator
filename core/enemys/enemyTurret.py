import math
from .enemyBase import EnemyBase
from core.utils import distance_to


class EnemyTurret(EnemyBase):
    def __init__(self, x, y,radius=2.0, health=150, fire_range=15):
        super().__init__(x, y, radius=radius, health=health, speed=0, etype="enemy_turret")
        self.fire_range = fire_range
      
        self.cooldown_timer = 0
        self.target = None
        
        self.health_max = 150
        self.cooldown_min = 5
        self.cooldown_max = 15

        self.last_health = self.health
        self.update_cooldown()
    
    def update(self, env):
        if self.health != self.last_health:
            self.update_cooldown()
            self.last_health = self.health

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return

        self.find_target(env)
        if self.target:
            self.shoot(env)
            
            

    def find_target(self, env):
        self.target = None
        for agent in env.agents:
            #print( distance_to(self, agent))
            if agent.alive and distance_to(self, agent) <= self.fire_range:
                self.target = agent
                
                break

    def shoot(self, env):
        if not self.target or not self.target.alive:
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        mag = math.hypot(dx, dy)
        if mag > 0:
            dx /= mag
            dy /= mag
        env.spawn_projectile(self.x, self.y, dx, dy,self)
        #env.spawn_smoke_zone(self.x, self.y, True,self)
        self.cooldown_timer = self.cooldown
        
    def update_cooldown(self):
        self.cooldown = self.cooldown_max - ((self.health / self.health_max) * (self.cooldown_max - self.cooldown_min))
