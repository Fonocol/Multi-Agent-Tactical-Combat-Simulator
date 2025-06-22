from typing import Any, Dict
from core.entity import Entity


class EnemyBase(Entity):
    def __init__(self, x, y, radius=3.0, health=100, speed=0.1, etype="enemy"):
        super().__init__(x, y, radius, etype=etype)
        self.health = health
        self.speed = speed
        self.alive = True

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            
  
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict() 
         
        data.update({
            'health':self.health
        })
        return data

    def update(self, env):
        raise NotImplementedError("Chaque type d'ennemi doit redéfinir update()")
