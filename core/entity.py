import uuid
from typing import Dict, Any

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
        


        

         
