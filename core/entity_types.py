
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

    @classmethod
    def all(cls):
        return [cls.AGENT, cls.TARGET, cls.DANGER, cls.ENERGY, cls.ENEMY, cls.PROJECTILE, cls.SMOKE, cls.JAMMER]
