import math

from core.entity_types import EntityType



def distance_to(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)

def is_blocked_by_wall(agent, target, walls):
    if target.etype == EntityType.WALL:
        return False
    for wall in walls:
        # Distance du mur à la ligne agent–target
        px, py = wall.x, wall.y
        ax, ay = agent.x, agent.y
        tx, ty = target.x, target.y

        # Projeter le mur sur le segment agent–target
        dx, dy = tx - ax, ty - ay
        mag = math.hypot(dx, dy)
        if mag == 0:
            continue

        dx /= mag
        dy /= mag

        # Projection du point mur sur la ligne agent–target
        t = ((px - ax) * dx + (py - ay) * dy)

        if t < 0 or t > mag:
            continue  # mur pas entre agent et target

        # Position du point projeté
        closest_x = ax + dx * t
        closest_y = ay + dy * t

        # Distance entre le mur et la ligne
        dist = math.hypot(px - closest_x, py - closest_y)

        if dist < wall.radius:
            return True  # Mur bloque la vue

    return False

