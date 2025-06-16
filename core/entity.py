import uuid

class Entity:
    def __init__(self, x, y, radius=1.0, etype="generic"):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.radius = radius
        self.etype = etype
        #self.active = True
        self.alive = True  # utile pour explosion/destruction

    def to_dict(self):
        return {
            "type": self.etype,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "alive": self.alive
        }
        


        

         
