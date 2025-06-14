from core.agents.combat_agents import GuardAgent, HeavyAgent, KamikazeAgent, ScoutAgent, SniperAgent, SupportAgent
from .enemys.enemyKamikaze import EnemyKamikaze
from .enemys.enemyTurret import EnemyTurret
from .enemys.enemy_drone import EnemyDrone
from core.objects.energy import EnergySource
from .enemys.mine import Mine
from core.objects.quest_item import ObjectiveItem
from core.objects.rockWall import RockWall
from core.objects.smoke_zone import JammerZone, SmokeZone

def spawn_objects():
    # Configuration des zones clés
    safe_zone = (15, 15)  # Zone de départ
    objective_south = (20, 80)  # Objectif principal
    objective_east = (80, 20)   # Objectif secondaire
    center = (50, 50)           # Point stratégique central
    
    return [
        # OBJECTIFS (positionnés asymétriquement)
        ObjectiveItem(*objective_south, radius=3),  # Objectif principal plus visible
        ObjectiveItem(*objective_east, radius=2.5), # Objectif secondaire
        
        # SOURCES D'ÉNERGIE (stratégiquement placées)
        EnergySource(*safe_zone, radius=3),          # Zone de départ
        EnergySource(85, 15, radius=2),             # Près de l'objectif Est (risqué)
        EnergySource(25, 70, radius=2),             # Sur le chemin de l'objectif Sud
        EnergySource(60, 40, radius=2.5),           # Point intermédiaire central
        
        # MINES (disposées en patterns stratégiques)
        *[Mine(x, y, trigger_radius=5)             # Champ de mines central
          for x in range(40, 61, 5)
          for y in range(40, 61, 5) if (x+y) % 7 != 0], # Pattern évitable
        
        Mine(18, 75, trigger_radius=8),            # Piège près objectif Sud
        Mine(75, 25, trigger_radius=6),            # Piège près objectif Est
        Mine(30, 30, trigger_radius=4),            # Piège sur route alternative
        
        # ENNEMIS MOBILES (avec rôles spécifiques)
        # Patrouilleurs centraux
        EnemyDrone(*center, patrol_radius=15, patrol_type='lemniscate'), # Gardien central
        EnemyDrone(40, 40, patrol_radius=8, patrol_type="spiral"),       # Défenseur zone
        
        # Patrouilleurs périphériques
        EnemyDrone(20, 50, patrol_radius=12, patrol_type='ellipse'),     # Flanc Sud
        EnemyDrone(70, 30, patrol_radius=10, patrol_type='square'),      # Flanc Est
        
        # Chasseurs aléatoires
        EnemyDrone(60, 60, patrol_radius=20, patrol_type='random'),      # Imprévisible
        EnemyDrone(30, 70, patrol_radius=5, patrol_type='random'),       # Près objectif
        
        # TOURELLES FIXES (points de contrôle)
        EnemyTurret(*center, radius=3, fire_range=25),                   # Contrôle central
        EnemyTurret(70, 30, radius=2.5),                                 # Couloir Est
        EnemyTurret(30, 70, radius=2.5),                                 # Approche Sud
        
        # ENNEMIS KAMIKAZES (embuscades)
        *[EnemyKamikaze(x, 75, radius=2.2) for x in range(15, 26, 5)],   # Ligne Sud
        EnemyKamikaze(65, 35, radius=2.2),                               # Zone Est
        EnemyKamikaze(45, 55, radius=2.2),                              # Centre
        
        # ZONES SPÉCIALES
        # Brouilleurs (désactivent les capacités)
        JammerZone(55, 55, radius=5),                   # Centre stratégique
        JammerZone(20, 60, radius=4),                   # Route Sud
        JammerZone(70, 40, radius=4),                   # Route Est
        
        # Fumée (obscurcissement visuel)
        SmokeZone(35, 50, radius=8),                    # Cache approche Sud
        SmokeZone(65, 35, radius=6),                   # Cache objectif Est
        SmokeZone(45, 45, radius=10),                   # Grande zone centrale
        
        # OBSTACLES NATURELS
        # Mur en L avec passage secret
        *[RockWall(x, 30, radius=1.8) for x in range(20, 41) if x != 30],
        *[RockWall(30, y, radius=1.8) for y in range(30, 51) if y != 40],
        
        # Blocs dispersés
        *[RockWall(x, y, radius=2) 
          for x in range(60, 76, 3) 
          for y in range(60, 76, 3) if (x+y) % 4 == 0],
    ]

def spawn_agent():
    return [
        ScoutAgent(10, 10),       
        SniperAgent(90, 90),      
        GuardAgent(12, 18, guard_x=12, guard_y=18),  
        KamikazeAgent(80, 20),    
        SupportAgent(8, 80),      
        HeavyAgent(25, 60)        
    ]

