from core.entity import Entity

class SmokeZone(Entity):
    def __init__(self, x, y, radius=5.0):
        super().__init__(x, y, radius, etype="smoke")
        self.vision_penalty = 0.5  # Réduit la range de vision à 50%
        
    def get_vision_penalty(self):
        return self.vision_penalty

#bloc la vision
class JammerZone(Entity):  
    def __init__(self, x, y, radius=6.0):
        super().__init__(x, y, radius, etype="jammer")
        self.block_vision = True


