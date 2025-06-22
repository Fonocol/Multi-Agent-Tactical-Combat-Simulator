import uuid
from typing import Dict, Any

import numpy as np

class Entity:
    def __init__(self, x:float, y:float, radius:float=1.0, etype:str="generic"):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.radius = radius
        self.etype = etype
        #self.active = True
        self.alive = True  # utile pour explosion/destruction


    def to_dict(self)-> Dict[str, Any]:
        return {
            "type": self.etype,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "alive": self.alive
        }
        
    def relative_position(self,other):
        dx = other.x - self.x
        dy = other.y - self.y
        vec = np.array([dx, dy])
        norm = np.linalg.norm(vec)

        if norm != 0:
            dx, dy = dx / norm, dy / norm

        return {
            "haut_droite": dx > 0 and dy > 0,
            "bas_droite": dx > 0 and dy < 0,
            "bas_gauche": dx < 0 and dy < 0,
            "haut_gauche": dx < 0 and dy > 0
        }

        


        

         
