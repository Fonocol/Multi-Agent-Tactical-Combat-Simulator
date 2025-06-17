from core.entity import Entity

class Decoy(Entity):
    def __init__(self, x:float, y:float, lifespan:float=20,radius:float=0.8):
        super().__init__(x, y, radius=radius,etype='decoy')
        self.lifespan = lifespan
        self.creation_time = 0  # à mettre à jour dans l'env

    def update(self, env):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.alive = False
