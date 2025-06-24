import numpy as np
import math
from core.agents.agent import Agent
from core.entity_types import EntityType

channels = {
    "agent": 0,
    "ally_agent": 1,
    "enemy_drone": 2,
    "enemy_kamikaze": 3,
    "energy": 4,
    "mine": 5,
    "enemy_drone_elite": 6,
    "enemy_turret": 7,
    "target": 8,
    "jammer": 9,
    "smoke": 9,
    "jammer_comunication": 10,
    "wall": 11,
    "facing": 12,
    "heatmap_danger": 13,
    "heatmap_energy": 14,
    "projectile_ally": 15,
    "projectile_enemy": 16,
    "decoy": 17,
}

channel_names = [
    "Agent", "Ally Agent", "Enemy Drone", "Kamikaze", "Energy", "Mine", "Drone Elite",
    "Turret", "Target", "Jammer/Smoke", "Jammer Com", "Wall", "Facing",
    "Heatmap Danger", "Heatmap Energy", "projectile_ally","projectile_enemy", "Decoy"
]

def extract_minimap_tensor(agent: Agent, env, grid_size=32):
    tensor = np.zeros((len(channel_names), grid_size, grid_size), dtype=np.float32)

    ax, ay = agent.x, agent.y
    vision_range = agent.range
    angle = agent.facing_angle
    center = grid_size // 2
    cell_size = (2 * vision_range) / grid_size

    def to_grid_coords(x, y):
        dx = x - ax
        dy = y - ay
        gx = int((dx + vision_range) / cell_size)
        gy = int((dy + vision_range) / cell_size)
        return gx, gy

    # Corps de l'agent au centre
    radius_cells = max(1, int(agent.radius / cell_size))
    for dx in range(-radius_cells, radius_cells + 1):
        for dy in range(-radius_cells, radius_cells + 1):
            x, y = center + dx, center + dy
            if 0 <= x < grid_size and 0 <= y < grid_size and dx**2 + dy**2 <= radius_cells**2:
                tensor[channels["agent"], y, x] = 1.0

    #  Regard de l'agent
    for i in range(1, center):
        dx = math.cos(angle) * i
        dy = math.sin(angle) * i
        gx = int(center + dx)
        gy = int(center + dy)
        if 0 <= gx < grid_size and 0 <= gy < grid_size:
            tensor[channels["facing"], gy, gx] = 1.0 - (i / center)

    # Objets visibles
    other_agents = [a for a in env.agents if a != agent and a.alive]
    visible_objects = agent.get_vision(env.objects + other_agents)

    for obj in visible_objects:
        ox, oy = obj.x, obj.y
        radius = getattr(obj, "radius", 1.0)
        
        if getattr(obj, "etype", None) == "projectile":
            if obj.owner is agent or getattr(obj.owner, "etype", None) == EntityType.AGENT:
                cls = "projectile_ally"
            else:
                cls = "projectile_enemy"
        else:
            cls = obj.etype if obj.etype != "agent" else "ally_agent"  # Corriger les agents alliés

        if cls not in channels:
            continue


        gx, gy = to_grid_coords(ox, oy)
        ch = channels[cls]
        radius_cells = max(1, int(radius / cell_size))

        value = 1.0
        if hasattr(obj, "health"):
            value = obj.health / 100.0
        elif cls == "energy" and hasattr(obj, "energy"):
            value = min(1.0, obj.energy / 100.0)
        elif cls == "mine":
            value = min(1.0, obj.explosion_radius / 4.0)
        elif cls in ["projectile", "decoy"]:
            value = 0.7

        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                x, y = gx + dx, gy + dy
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    if dx**2 + dy**2 <= radius_cells**2:
                        tensor[ch, y, x] = max(tensor[ch, y, x], value)

                        # Heatmap danger
                        if cls in ["enemy_drone", "enemy_kamikaze", "enemy_turret", "mine", "enemy_drone_elite","projectile_enemy"]:
                            tensor[channels["heatmap_danger"], y, x] = max(
                                tensor[channels["heatmap_danger"], y, x], value)

                        # Heatmap énergie
                        if cls == "energy":
                            tensor[channels["heatmap_energy"], y, x] = max(
                                tensor[channels["heatmap_energy"], y, x], value)

    return tensor
