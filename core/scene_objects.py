from collections import defaultdict
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
    safe_zone = (15, 15)
    objective_south = (25, 85)
    objective_east = (85, 25)
    center = (50, 50)

    return [
        # OBJECTIFS
        ObjectiveItem(*objective_south, radius=3.5),
        ObjectiveItem(*objective_east, radius=3.0),

        # ÉNERGIE – sur les chemins stratégiques
        EnergySource(*safe_zone, radius=3.0),
        EnergySource(25, 65, radius=2.5,energy=100),  # En route vers objectif Sud
        EnergySource(65, 25, radius=2.5,energy=70),  # En route vers objectif Est
        EnergySource(50, 50, radius=2.0),  # Milieu central

        # MINES – bloquent les chemins directs
        *[Mine(x, y, trigger_radius=1.8) for x, y in [
            (40, 50), (60, 50), (50, 40), (50, 60),
            (30, 80), (80, 30)
        ]],

        # DRONES – placés pour intercepter
        EnemyDrone(40, 45, patrol_radius=20, radius=1.6,role=Role.SMOKER,patrol_type='square'),
        EnemyDrone(60, 55, patrol_radius=10, radius=1.6),
        EnemyDrone(30, 70, patrol_radius=8, radius=1.6, patrol_type="lemniscate"),
        EliteDrone(70, 30, patrol_radius=10, radius=10),
        EliteDrone(25, 25, patrol_radius=8, radius=8,role=Role.JammerComunication,patrol_type='random'),

        # TOURELLES – protègent les objectifs
        EnemyTurret(35, 85, fire_range=15, radius=3.0, health=50),  # Objectif Sud
        EnemyTurret(85, 35, fire_range=15, radius=3.0),             # Objectif Est

        # KAMIKAZES – embuscades en bordure
        *[EnemyKamikaze(x, 70, radius=2.0) for x in (20, 25, 30)],
        *[EnemyKamikaze(70, y, radius=2.0) for y in (20, 25, 30)],

        # ZONES SPÉCIALES – perturbation stratégique
        JammerZone(50, 50, radius=6.0, moving=True, ttl=1000),
        SmokeZone(35, 85, radius=6.0),  # Cache Sud
        SmokeZone(85, 35, radius=6.0),  # Cache Est

        # OBSTACLES – forme de croix au centre
        *[RockWall(x, 50, radius=2.0) for x in range(40, 61, 5)],
        *[RockWall(50, y, radius=2.0) for y in range(40, 61, 5)],
    ]



# def spawn_objects():
#     # Points clés avec marges des bords
#     safe_zone = (15, 15)
#     objective_south = (25, 85)  # 15 unités du bord
#     objective_east = (85, 25)   # 15 unités du bord
#     center = (50, 50)
    
#     return [
#         # *[EnemyKamikaze(20 + x, 80, radius=2.0) for x in range(0, 15, 5)],
#         *[EnemyKamikaze(80, 20 + y, radius=2.0) for y in range(0, 15, 5)],
#         EnemyTurret(50, 50, radius=3.0, fire_range=50),
#         EnemyTurret(50, 40, radius=3.0, fire_range=50,health=20),
#         SoldierEnemy(12, 12, radius=1.0),
       
#     ]

    
def spawn_agent(use_rl=False):
    agents = []

    # Agent RL à entraîner : position aléatoire dans une zone centrale
    if use_rl:
        rl_x = np.random.randint(25, 75)
        rl_y = np.random.randint(25, 75)
        agents.append(RLScoutAgent(rl_x, rl_y, radius=1.2))
    else:

        agents.append(ScoutAgent(50, 30, radius=1.2))  # agent test/démo

    # Agents NON-RL (randomisés mais avec des rôles clairs)
    agents.extend([
        ScoutAgent(np.random.randint(20, 80), np.random.randint(10, 30), radius=1.2),     # éclaireur secondaire
        SniperAgent(10,10, radius=1.5, range_radius=40),  # zone haute
        GuardAgent(np.random.randint(10, 20), np.random.randint(10, 20), radius=1.8),     # garde base
        SupportAgent(np.random.randint(20, 35), np.random.randint(15, 30), radius=1.3),   # soigneur
        HeavyAgent(np.random.randint(70, 90), np.random.randint(40, 60), radius=2.2),     # tank position
        KamikazeAgent(80, 80, radius=1.8)  # activable selon scénario
    ])

    return agents


