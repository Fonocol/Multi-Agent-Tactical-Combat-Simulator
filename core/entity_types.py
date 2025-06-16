
class EntityType:
    AGENT = "agent"
    TARGET = "target"
    DANGER = "danger"
    ENERGY = "energy"
    ENEMY = "enemy"
    PROJECTILE = "projectile"
    SMOKE = "smoke"
    JAMMER = "jammer"
    ENERGY_DRONE="enemy_drone"
    ENERGY_KAMIKAZE='enemy_kamikaze'
    WALL= 'wall'
    JammerComunication = 'jammer_comunication'

    @classmethod
    def all(cls):
        return [cls.AGENT, cls.TARGET, cls.DANGER, cls.ENERGY, cls.ENEMY, cls.PROJECTILE, cls.SMOKE, 
                cls.JAMMER, cls.ENERGY_DRONE,  cls.ENERGY_KAMIKAZE,   cls.WALL, cls.JammerComunication]


class Role:
    JammerComunication = 'jammer_comunication',
    SMOKER = 'smoker'

    @classmethod
    def all(cls):
        return [cls.JammerComunication,cls.SMOKER]
