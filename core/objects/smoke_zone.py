from core.entity import Entity
from core.entity_types import EntityType
from core.objects.objectBase import ObjectBase

#self, x, y, radius=3.0, speed=0.1, etype="object",moving=False, ttl=15


class SmokeZone(ObjectBase):
    def __init__(self, x, y, radius=5.0,moving=False, ttl=15, speed=1.5):
        super().__init__(x, y, radius=radius,speed=speed,moving=moving ,etype=EntityType.SMOKE,ttl=ttl)
        self.vision_penalty = 0.8  # Réduit la range de vision à 80%

        
    def get_vision_penalty(self):
        return self.vision_penalty
    
   
#bloc la vision
class JammerZone(ObjectBase):  
    def __init__(self, x, y, radius=6.0,moving=False, ttl=15, speed=1.5):
        super().__init__(x, y, radius=radius,speed=speed,moving=moving ,etype=EntityType.JAMMER,ttl=ttl)
        self.block_vision = True

               
class JammerCommunication(ObjectBase):
    def __init__(self, x, y, radius=20.0, moving=False, speed=1.5, ttl=15):
        super().__init__(x, y, radius=radius, speed=speed, moving=moving, etype=EntityType.JammerComunication, ttl=ttl)





