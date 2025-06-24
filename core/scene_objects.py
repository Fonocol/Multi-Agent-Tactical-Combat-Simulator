from collections import defaultdict
import random
from typing import Dict, List

import numpy as np
from core.agents.combat_agents import GuardAgent, HeavyAgent, KamikazeAgent, ScoutAgent, SniperAgent, SupportAgent
from core.agents.rl_agents.rl_scout import RLScoutAgent
from core.enemys.elite_drone import EliteDrone
from core.enemys.soldierEnemy import SoldierEnemy
from core.entity import Entity
from core.entity_types import EntityType, Role
from .enemys.enemyKamikaze import EnemyKamikaze
from .enemys.enemyTurret import EnemyTurret
from .enemys.enemy_drone import EnemyDrone
from core.objects.energy import EnergySource
from .enemys.mine import Mine
from core.objects.quest_item import ObjectiveItem
from core.objects.rockWall import RockWall
from core.objects.smoke_zone import JammerZone, SmokeZone


def spawn_objects():
    safe_zone = (50, 450)
    objective_south = (100, 480)
    objective_east = (480, 100)
    center = (250, 250)

    def scaled_circle_grid(start_x, start_y, spacing, count, radius):
        return [RockWall(start_x + i * spacing, start_y + j * spacing, radius=radius)
                for i in range(count) for j in range(count)]

    objects = [
        # 🎯 OBJECTIFS
        ObjectiveItem(*objective_south, radius=6.0),
        ObjectiveItem(*objective_east, radius=6.0),

        # 🔋 ÉNERGIE
        EnergySource(*safe_zone, radius=4.0, energy=100),
        EnergySource(150, 400, radius=4.0, energy=120),
        EnergySource(400, 150, radius=4.0, energy=90),
        EnergySource(*center, radius=20.0, energy=50),

        # 💣 MINES
        *[Mine(x, y, trigger_radius=2.0, explosion_radius=np.random.randint(5, 8)) for x, y in [
            (220, 250), (280, 250), (250, 220), (250, 280),
            (180, 420), (420, 180)
        ]],

        # ✈️ DRONES
        EnemyDrone(100, 100, patrol_radius=90, radius=2.2, role=Role.SMOKER, patrol_type='square'),
        EnemyDrone(400, 400, patrol_radius=80, radius=2.2,role=EntityType.JammerComunication),
        EnemyDrone(350, 150, patrol_radius=60, radius=2.2, patrol_type="lemniscate"),
        EliteDrone(100, 300, patrol_radius=40, radius=2.5,patrol_type='square_random'),
        EliteDrone(250, 250, patrol_radius=20, radius=2.0, role=Role.JammerComunication, patrol_type='random'),

        # 🛡️ TOURELLES
        EnemyTurret(130, 470, fire_range=60, radius=8.0, health=80),
        EnemyTurret(130, 130, fire_range=50, radius=10.0),

        # 💥 KAMIKAZES
        *[EnemyKamikaze(x, 380, radius=3.0) for x in (80, 100, 120)],
        *[EnemyKamikaze(380, y, radius=3.0) for y in (80, 100, 120)],

        # 🌫️ ZONES SPÉCIALES
        JammerZone(*center, radius=22.0, moving=True, ttl=2000),
        SmokeZone(170, 460, radius=10.0),
        SmokeZone(460, 170, radius=10.0),

        # 🧱 OBSTACLES : croix centrale + murs verticaux
        *[RockWall(x, 300, radius=3.0) for x in range(250, 350, 20)],
        *[RockWall(300, y, radius=3.0) for y in range(250, 350, 20)],

        # Grille urbaine style "quartier"
        *scaled_circle_grid(100, 100, spacing=40, count=5, radius=2.0)
    ]

    return objects

    
def spawn_agent(use_rl=True):
    agents = []
    start_zones = [(250, 70), (70, 250), (250, 400), (400, 250)]
    start_x, start_y = random.choice(start_zones)

    if use_rl:
        agents.append(RLScoutAgent(start_x, start_y, radius=1.5))
    else:
        agents.append(ScoutAgent(start_x, start_y, radius=1.5))

    if not use_rl:
        agents.extend([
            HeavyAgent(50, 150, radius=3.0),
            SupportAgent(220, 450, radius=2.2),
            SniperAgent(350, 350, radius=2.0, range_radius=80),
            ScoutAgent(480, 480, radius=1.5)
        ])

    return agents
