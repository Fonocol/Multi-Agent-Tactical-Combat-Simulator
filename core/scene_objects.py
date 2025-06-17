from core.agents.combat_agents import GuardAgent, HeavyAgent, KamikazeAgent, ScoutAgent, SniperAgent, SupportAgent
from core.enemys.elite_drone import EliteDrone
from core.entity_types import Role
from .enemys.enemyKamikaze import EnemyKamikaze
from .enemys.enemyTurret import EnemyTurret
from .enemys.enemy_drone import EnemyDrone
from core.objects.energy import EnergySource
from .enemys.mine import Mine
from core.objects.quest_item import ObjectiveItem
from core.objects.rockWall import RockWall
from core.objects.smoke_zone import JammerZone, SmokeZone

def spawn_objects():
    # Points clés avec marges des bords
    safe_zone = (15, 15)
    objective_south = (25, 85)  # 15 unités du bord
    objective_east = (85, 25)   # 15 unités du bord
    center = (50, 50)
    
    return [
        # OBJECTIFS
        ObjectiveItem(*objective_south, radius=3.5),  # Taille augmentée
        ObjectiveItem(*objective_east, radius=3.0),
        
        # ÉNERGIE - positions plus stratégiques
        EnergySource(*safe_zone, radius=3.0),
        EnergySource(80, 20, radius=2.5),  # Chemin vers objectif Est
        EnergySource(20, 75, radius=2.5),  # Chemin vers objectif Sud
        EnergySource(55, 45, radius=2.0),  # Point intermédiaire
        
        # MINES - moins nombreuses mais mieux placées
        *[Mine(x, y, trigger_radius=1.8) for x,y in [
            (45,45), (50,50), (55,55),  # Diagonale centrale
            (20,70), (70,20),           # Approches objectives
            (30,30), (70,70)            # Zones alternatives
        ]],
        
        # DRONES - nombre réduit mais plus efficaces
        EliteDrone(20,20, patrol_radius=12, radius=1.8),
        EnemyDrone(*center, patrol_radius=12, radius=1.8),
        EnemyDrone(35, 65, patrol_radius=8, radius=1.6,patrol_type='lemniscate'),
        EnemyDrone(65, 35, patrol_radius=8, radius=1.6,patrol_type='random'),
        EnemyDrone(12, 12, patrol_radius=5, radius=1.6,patrol_type='square',role=Role.JammerComunication),
        
        # # TOURELLES - positions clés
        EnemyTurret(40, 60, radius=3.0, fire_range=20,health=50),  # Protège objectif Sud
        EnemyTurret(60, 40, radius=3.0, fire_range=10),  # Protège objectif Est
        
        # KAMIKAZES - groupes compacts
        *[EnemyKamikaze(20 + x, 80, radius=2.0) for x in range(0, 15, 5)],
        *[EnemyKamikaze(80, 20 + y, radius=2.0) for y in range(0, 15, 5)],
        
        # ZONES SPÉCIALES
        JammerZone(50, 50, radius=6.0,moving=True,ttl=1000),  # Centre élargi
        SmokeZone(40, 60, radius=7.0,moving=True),   # Cache objectif Sud
        SmokeZone(60, 40, radius=7.0),   # Cache objectif Est
        
        # OBSTACLES
        *[RockWall(x, 40, radius=2.0) for x in range(30, 71, 10)],
        *[RockWall(40, y, radius=2.0) for y in range(30, 71, 10)],
        *[RockWall(x, y, radius=1.5) 
          for x in range(70, 86, 5) 
          for y in range(70, 86, 5) if (x + y) % 3 == 0],
        EliteDrone(30,30, patrol_radius=12, radius=1.8,patrol_type='square'),
    ]

def spawn_agent():
    return [
        ScoutAgent(12, 12, radius=1.2),       # Proche safe zone
        SniperAgent(85, 85, radius=1.5),      # Position avancée
        GuardAgent(15, 15, radius=1.8),       # Protection base
        SupportAgent(20, 20, radius=1.3),     # Support arrière
        HeavyAgent(25, 25, radius=2.2),       # Défense rapprochée
        KamikazeAgent(80, 80, radius=1.8)     # Attaque frontale
    ]
