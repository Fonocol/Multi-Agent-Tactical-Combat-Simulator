import numpy as np
from core.entity_types import EntityType
MAX_DRONES = 50
MAX_DRONES_ELITE=3

def distance_to(self, obj) -> float:
    return np.linalg.norm(np.array([obj.x, obj.y]) - np.array([self.x, self.y]))


def is_blocked_by_wall(agent, target, walls):
    if target.etype == EntityType.WALL:
        return False

    a = np.array([agent.x, agent.y])
    t = np.array([target.x, target.y])
    ab = t - a
    mag = np.linalg.norm(ab)

    if mag == 0:
        return False

    ab_dir = ab / mag  # vecteur direction normalisé

    for wall in walls:
        p = np.array([wall.x, wall.y])
        
        ap = p - a
        proj_length = np.dot(ap, ab_dir)

        if proj_length < 0 or proj_length > mag:
            continue  # mur pas entre agent et target

        # Projection sur la ligne
        closest_point = a + proj_length * ab_dir
        dist_to_line = np.linalg.norm(p - closest_point)

        if dist_to_line < wall.radius:
            return True  # le mur bloque

    return False


def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

   
    
    
