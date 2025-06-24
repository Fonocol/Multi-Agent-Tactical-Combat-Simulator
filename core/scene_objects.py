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
    safe_zone = (15, 15)
    objective_south = (25, 85)
    objective_east = (85, 25)
    center = (50, 50)

    objects = [
        # 🎯 OBJECTIFS
        ObjectiveItem(*objective_south, radius=3.0),
        ObjectiveItem(*objective_east, radius=3.0),

        # 🔋 ÉNERGIE – sur les routes clés
        EnergySource(*safe_zone, radius=2.8,energy=80),
        EnergySource(25, 65, radius=2.5, energy=100),
        EnergySource(65, 25, radius=2.5, energy=70),
        EnergySource(*center, radius=2.0,energy=20),

        # 💣 MINES – bloquent les accès directs
        *[Mine(x, y, trigger_radius=1.5,explosion_radius=np.random.randint(2,4)) for x, y in [
            (42, 50), (58, 50), (50, 42), (50, 58),
            (30, 78), (78, 30)
        ]],

        # ✈️ DRONES – patrouilles d'interception
        EnemyDrone(40, 80, patrol_radius=18, radius=1.6, role=Role.SMOKER, patrol_type='square'),
        EnemyDrone(89, 80, patrol_radius=10, radius=1.6),
        EnemyDrone(30, 70, patrol_radius=8, radius=1.6, patrol_type="lemniscate"),
        EliteDrone(70, 30, patrol_radius=10, radius=2.0),
        EliteDrone(10, 10, patrol_radius=8, radius=1.5, role=Role.JammerComunication, patrol_type='random'),

        # 🛡️ TOURELLES – défenses proches des objectifs
        EnemyTurret(32, 82, fire_range=14, radius=2.5, health=50),
        EnemyTurret(82, 32, fire_range=14, radius=2.5),

        # 💥 KAMIKAZES – embuscades
        *[EnemyKamikaze(x, 68, radius=2.0) for x in (20, 25, 30)],
        *[EnemyKamikaze(68, y, radius=2.0) for y in (20, 25, 30)],

        # 🌫️ ZONES SPÉCIALES
        JammerZone(*center, radius=6.0, moving=True, ttl=1000),
        SmokeZone(35, 80, radius=5.0),
        SmokeZone(80, 35, radius=5.0),

        # 🧱 OBSTACLES – croix centrale + couloirs verticaux
        *[RockWall(x, 60, radius=1.8) for x in range(50, 71, 5)],
        *[RockWall(60, y, radius=1.8) for y in range(50, 71, 5)],
    ]

    # 🧱 Murs verticaux Nord-Est / Nord-Ouest
    for x in [40, 60]:
        for y in range(10, 40, 5):
            objects.append(RockWall(x, y, radius=1.8))

    return objects


def spawn_agent(use_rl=True):
    agents = []
    start_zones = [(10,40), (20,40), (20,40), (70,70), (90,10)]
    start_x, start_y = random.choice(start_zones)
    
    if use_rl:
        # Position de départ aléatoire mais sécurisée    
        agents.append(RLScoutAgent(start_x, start_y, radius=1.2))
    else:
        # Pour démo/test - position centrale
        agents.append(ScoutAgent(start_x, start_y, radius=1.2))
    
    # Eventuels autres agents
    # if not use_rl:
    #     agents.extend([
    #         HeavyAgent(20, 80, radius=2.0),
    #         SupportAgent(80, 20, radius=1.5),
    #         SniperAgent(10, 90, radius=1.3, range_radius=35)
    #     ])
    
    return agents

