from core.entity_types import  EntityType, Role
from .enemyBase import EnemyBase
from core.utils import MAX_DRONES_ELITE, distance_to
import math
import random
from enum import Enum

class DroneStrategy(Enum):
    AGGRESSIVE = 1
    CAUTIOUS = 2
    EVASIVE = 3
    FLANKER = 4
    TRICKSTER = 5

class EliteDrone(EnemyBase):
    DRONE_TRAITS = {
        'speed': (0.05, 0.2),
        'fire_rate': (0.5, 2.0),
        'evasiveness': (0.0, 1.0),
        'swarm_aggression': (0.0, 1.0),
        'intelligence': (0.5, 1.5)
    }

    def __init__(self, x, y, patrol_radius=10, radius=3.0, fire_range=10.0, patrol_type="circle", role:str='any', dna=None):
        super().__init__(x, y, radius=radius, health=100, speed=0.1, etype=EntityType.ENERGY_DRONE_ELITE)
        
        # Configuration de base
        self.patrol_radius = patrol_radius
        self.center = (x, y)
        self.angle = 0.0
        self.attack_range = 15.0
        self.fire_range = fire_range
        self.target = None
        self.patrol_type = patrol_type.lower()
        self.role = role.lower()
        
        self.last_reproduction_time = 0
        self.reproduction_cooldown = 50  # ticks minimum entre deux repros
        self.health_cost = 20
        
        # Comportement aléatoire
        self.random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
        self.random_timer = 0
        
        # Intelligence et adaptation
        self.adaptation_timer = 0
        self.learned_behaviors = {
            DroneStrategy.AGGRESSIVE: 0.5,
            DroneStrategy.CAUTIOUS: 0.5,
            DroneStrategy.EVASIVE: 0.5,
            DroneStrategy.FLANKER: 0.3,
            DroneStrategy.TRICKSTER: 0.2
        }
        self.current_strategy = self._choose_strategy()
        
        # Motifs de mouvement
        self.pattern_mixer = {
            'base_pattern': self.patrol_type,
            'current_mix': 0,
            'mix_target': random.choice(["circle", "lemniscate", "random", "square"]),
            'mix_duration': random.randint(200, 500)
        }
        
        # Génétique
        self.dna = dna or self._random_dna()
        self._apply_dna()
        
        # Mémoire
        self.last_known_target_pos = None
        self.failed_attacks = 0

    def _random_dna(self):
        return {trait: random.uniform(*range) 
               for trait, range in self.DRONE_TRAITS.items()}
               
    def _apply_dna(self):
        self.speed *= self.dna['speed']
        self.evasiveness = self.dna['evasiveness']
        self.attack_range *= self.dna['intelligence']
        self.fire_range *= self.dna['intelligence']

    def _choose_strategy(self):
        strategies = list(self.learned_behaviors.keys())
        weights = list(self.learned_behaviors.values())
        return random.choices(strategies, weights=weights)[0]

    def update(self, env):
        # Communication entre drones et swarm intelligence
        nearby_drones = self._get_nearby_drones(env)
        if nearby_drones:
            self._swarm_behavior(nearby_drones)
        
        # Adaptation et apprentissage
        self.adaptation_timer += 1
        if self.adaptation_timer > 300:
            self._adapt_strategy(env)
            self.adaptation_timer = 0
        
        # Recherche de cible améliorée
        self._find_target(env)
        
        if self.target:
            self._chase_or_attack(env)
        else:
            self._advanced_patrol()
            
        # Reproduction occasionnelle
        self._maybe_reproduce(env)

    def _get_nearby_drones(self, env):
        
        return [e for e in env.objects 
                if e != self and isinstance(e, EliteDrone) 
                and distance_to(self, e) < 20 * self.dna['swarm_aggression']]

    def _swarm_behavior(self, nearby_drones):
        # Partage d'information sur les cibles
        shared_targets = [d.target for d in nearby_drones if d.target]
        if shared_targets and (not self.target or random.random() < 0.4):
            self.target = max(shared_targets, key=lambda t: sum(1 for d in nearby_drones if d.target == t))
        
        # Comportement de swarm
        if len(nearby_drones) > 2 and self.dna['swarm_aggression'] > 0.3:
            avg_x = sum(d.x for d in nearby_drones) / len(nearby_drones)
            avg_y = sum(d.y for d in nearby_drones) / len(nearby_drones)
            
            # Maintenir une formation avec distance optimale
            cohesion_factor = 0.02 * self.dna['swarm_aggression']
            self.x += (avg_x - self.x) * cohesion_factor
            self.y += (avg_y - self.y) * cohesion_factor
            
            # Éviter les collisions
            for drone in nearby_drones:
                dist = distance_to(self, drone)
                if dist < self.radius * 2:
                    repel_factor = 0.05 * self.evasiveness
                    self.x -= (drone.x - self.x) * repel_factor
                    self.y -= (drone.y - self.y) * repel_factor

    def _adapt_strategy(self, env):
        # Analyse de l'environnement
        nearby_threats = sum(1 for e in env.objects 
                            if hasattr(e, 'is_hostile') and e.is_hostile 
                            and distance_to(self, e) < 15)
        
        # Ajustement des stratégies basé sur l'expérience
        if nearby_threats > 3:
            self.learned_behaviors[DroneStrategy.EVASIVE] += 0.2
            self.learned_behaviors[DroneStrategy.AGGRESSIVE] -= 0.1
        elif self.health < 50:
            self.learned_behaviors[DroneStrategy.CAUTIOUS] += 0.3
            self.learned_behaviors[DroneStrategy.TRICKSTER] += 0.1
        
        if self.failed_attacks > 5:
            self.learned_behaviors[DroneStrategy.FLANKER] += 0.2
            self.learned_behaviors[DroneStrategy.TRICKSTER] += 0.1
            self.failed_attacks = 0
        
        # Normalisation
        total = sum(self.learned_behaviors.values())
        for k in self.learned_behaviors:
            self.learned_behaviors[k] /= total
        
        self.current_strategy = self._choose_strategy()

    def _find_target(self, env):
        self.target = None
        best_target = None
        best_score = -1
        
        for agent in env.agents:
            if agent.alive:
                dist = distance_to(self, agent)
                if dist <= self.attack_range * (1.2 if self.current_strategy == DroneStrategy.AGGRESSIVE else 1.0):
                    # Score basé sur la distance, la santé et la stratégie
                    score = (1 - dist/self.attack_range) * 0.6
                    score += (1 - agent.health/agent.max_health) * 0.4 if hasattr(agent, 'max_health') else 0
                    
                    if self.current_strategy == DroneStrategy.CAUTIOUS:
                        score *= (agent.health/agent.max_health) if hasattr(agent, 'max_health') else 1
                    
                    if score > best_score:
                        best_score = score
                        best_target = agent
        
        self.target = best_target
        if self.target:
            self.last_known_target_pos = (self.target.x, self.target.y)

    def _chase_or_attack(self, env):
        if not self.target or not self.target.alive:
            self.target = None
            return
        
        dist = distance_to(self, self.target)
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        mag = math.hypot(dx, dy)
        
        if mag > 0:
            dx /= mag
            dy /= mag
            
        # Comportement selon la stratégie choisie
        if self.current_strategy == DroneStrategy.FLANKER:
            self._flanker_behavior(dx, dy, dist)
        elif self.current_strategy == DroneStrategy.TRICKSTER:
            self._trickster_behavior(env, dx, dy, dist)
        elif self.current_strategy == DroneStrategy.EVASIVE:
            self._evasive_behavior(env, dx, dy, dist)
        else:  # AGGRESSIVE ou CAUTIOUS
            self._standard_behavior(env, dx, dy, dist)

    def _flanker_behavior(self, dx, dy, dist):
        # Mouvement de flanquement
        perp_dx = -dy * (0.5 + 0.3 * math.sin(self.angle))
        perp_dy = dx * (0.5 + 0.3 * math.cos(self.angle))
        
        approach_speed = self.speed * (2 if dist > self.fire_range else 1)
        self.x += (dx * 0.7 + perp_dx) * approach_speed
        self.y += (dy * 0.7 + perp_dy) * approach_speed
        self.angle += 0.1

    def _trickster_behavior(self, env, dx, dy, dist):
        # Leurres et fausses retraites
        if random.random() < 0.05 + 0.1 * self.evasiveness:
            if dist < self.fire_range * 0.7:
                # Fausse retraite
                self.x -= dx * self.speed * (3 + self.evasiveness)
                self.y -= dy * self.speed * (3 + self.evasiveness)
                # Laisse un leurre
                if random.random() < 0.7:
                    env.spawn_decoy(self.x, self.y, lifespan=120)
                return
            elif dist > self.fire_range * 1.2:
                # Attaque feinte
                fake_dir = (math.cos(self.angle * 2), math.sin(self.angle * 2))
                env.spawn_projectile(self.x, self.y, *fake_dir, self)
                
        
        # Approche en zigzag
        zigzag = math.sin(env.time * 0.2) * 0.8
        self.x += (dx + zigzag * -dy) * self.speed * 1.2
        self.y += (dy + zigzag * dx) * self.speed * 1.2
        
        if dist <= self.fire_range * (0.9 + random.random() * 0.2):
            self._execute_attack(env, dx, dy)

    def _evasive_behavior(self, env, dx, dy, dist):
        # Mouvement erratique
        evasion = math.sin(env.time * 0.3) * self.evasiveness
        self.x += (dx * 0.5 + evasion * -dy) * self.speed
        self.y += (dy * 0.5 + evasion * dx) * self.speed
        
        # Tir rapide en mouvement
        if random.random() < 0.1 + 0.05 * self.dna['fire_rate'] and dist < self.fire_range * 1.3:
            self._execute_attack(env, dx, dy)

    def _standard_behavior(self, env, dx, dy, dist):
        if dist > self.fire_range * (0.8 if self.current_strategy == DroneStrategy.AGGRESSIVE else 1.1):
            # Approche
            approach_speed = self.speed * (1.5 if self.current_strategy == DroneStrategy.AGGRESSIVE else 1.0)
            self.x += dx * approach_speed
            self.y += dy * approach_speed
            
            # Spirale d'approche
            if self.current_strategy == DroneStrategy.AGGRESSIVE:
                spiral = math.sin(env.time * 0.15) * 0.4
                self.x += spiral * -dy
                self.y += spiral * dx
        else:
            # Attaque
            if self.current_strategy == DroneStrategy.CAUTIOUS and random.random() < 0.3:
                # Recul avant de tirer
                self.x -= dx * self.speed * 0.8
                self.y -= dy * self.speed * 0.8
            self._execute_attack(env, dx, dy)

    def _execute_attack(self, env, dx, dy):
        attack_success = False
        
        if self.role == Role.JammerComunication:
            env.spawn_jammer_communication(self.x, self.y, moving=True, owner=self)
            attack_success = True
        elif self.role == Role.SMOKER:
            env.spawn_smoke_zone(self.x, self.y, moving=True, owner=self)
            attack_success = True
        else:
            # Tir prédictif pour les cibles mobiles
            if hasattr(self.target, 'dx') and hasattr(self.target, 'dy'):
                lead_time = max(0.1, 1 - (distance_to(self, self.target) / self.fire_range))
                pred_dx = dx + self.target.dx * lead_time
                pred_dy = dy + self.target.dy * lead_time
                pred_mag = math.hypot(pred_dx, pred_dy)
                if pred_mag > 0:
                    pred_dx /= pred_mag
                    pred_dy /= pred_mag
                env.spawn_projectile(self.x, self.y, pred_dx, pred_dy, self)
                attack_success = pred_mag > 0
            else:
                env.spawn_projectile(self.x, self.y, dx, dy)
                attack_success = True
        
        if not attack_success:
            self.failed_attacks += 1

    def _advanced_patrol(self):
        # Transition progressive entre motifs
        if self.pattern_mixer['current_mix'] < self.pattern_mixer['mix_duration']:
            self.pattern_mixer['current_mix'] += 1
            mix_ratio = self.pattern_mixer['current_mix'] / self.pattern_mixer['mix_duration']
            
            # Exécute les deux motifs et interpole
            original_pos = self.x, self.y
            self._execute_single_pattern(self.pattern_mixer['base_pattern'])
            pos1 = self.x, self.y
            self.x, self.y = original_pos
            self._execute_single_pattern(self.pattern_mixer['mix_target'])
            pos2 = self.x, self.y
            
            self.x = pos1[0] * (1-mix_ratio) + pos2[0] * mix_ratio*2
            self.y = pos1[1] * (1-mix_ratio) + pos2[1] * mix_ratio*2
        else:
            # Change de motif
            self.pattern_mixer = {
                'base_pattern': self.pattern_mixer['mix_target'],
                'current_mix': 0,
                'mix_target': random.choice(["circle", "lemniscate", "random", "square", "ellipse"]),
                'mix_duration': random.randint(200, 500)
            }
            self._execute_single_pattern(self.pattern_mixer['base_pattern'])

    def _execute_single_pattern(self, pattern):
        self.angle += self.speed * (0.5 if "random" in pattern else 1.0)
        
        if pattern == "circle":
            self.x = self.center[0] + self.patrol_radius * math.cos(self.angle)
            self.y = self.center[1] + self.patrol_radius * math.sin(self.angle)
        elif pattern == "ellipse":
            a = self.patrol_radius
            b = self.patrol_radius * 0.6
            self.x = self.center[0] + a * math.cos(self.angle)
            self.y = self.center[1] + b * math.sin(self.angle)
        elif pattern == "lemniscate":
            a = self.patrol_radius
            scale = 0.5
            t = self.angle * 2
            denom = 1 + math.sin(t)**2
            r = (a * math.sqrt(2) * math.cos(t)) / denom
            self.x = self.center[0] + r * math.cos(t) * scale
            self.y = self.center[1] + r * math.sin(t) * scale
        elif pattern == "spiral":
            r = self.patrol_radius * (1 + 0.05 * (self.angle % (2*math.pi)))
            self.x = self.center[0] + r * math.cos(self.angle)
            self.y = self.center[1] + r * math.sin(self.angle)
        elif pattern == "random":
            self.random_timer += 1
            if self.random_timer > 60:
                self.random_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
                self.random_timer = 0
            self.x += self.random_direction[0] * self.speed
            self.y += self.random_direction[1] * self.speed
            dist_to_center = math.hypot(self.x - self.center[0], self.y - self.center[1])
            if dist_to_center > self.patrol_radius * 1.5:
                self.random_direction = (
                    (self.center[0] - self.x) / dist_to_center,
                    (self.center[1] - self.y) / dist_to_center
                )
        elif pattern == "square":
            half_size = self.patrol_radius
            corners = [
                (self.center[0] - half_size, self.center[1] - half_size),
                (self.center[0] + half_size, self.center[1] - half_size),
                (self.center[0] + half_size, self.center[1] + half_size),
                (self.center[0] - half_size, self.center[1] + half_size)
            ]
            corner_duration = math.pi/2
            current_corner_idx = int(self.angle // corner_duration) % 4
            next_corner_idx = (current_corner_idx + 1) % 4
            progress = (self.angle % corner_duration) / corner_duration
            start_x, start_y = corners[current_corner_idx]
            end_x, end_y = corners[next_corner_idx]
            self.x = start_x + (end_x - start_x) * progress
            self.y = start_y + (end_y - start_y) * progress
            self.angle += self.speed * 0.5
        elif pattern == "square_random":
            half_size = self.patrol_radius
            if not hasattr(self, 'square_target'):
                self.square_target = (
                    self.center[0] + random.uniform(-half_size, half_size),
                    self.center[1] + random.uniform(-half_size, half_size)
                )
            dx = self.square_target[0] - self.x
            dy = self.square_target[1] - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed * 2:
                self.square_target = (
                    self.center[0] + random.uniform(-half_size, half_size),
                    self.center[1] + random.uniform(-half_size, half_size)
                )
            elif dist > 0:
                dx /= dist
                dy /= dist
                self.x += dx * self.speed
                self.y += dy * self.speed
            self.x = max(self.center[0] - half_size, min(self.center[0] + half_size, self.x))
            self.y = max(self.center[1] - half_size, min(self.center[1] + half_size, self.y))
        else:  # Default to circle
            self.x = self.center[0] + self.patrol_radius * math.cos(self.angle)
            self.y = self.center[1] + self.patrol_radius * math.sin(self.angle)

    
        
            
    def _maybe_reproduce(self, env):
                num_drones = sum(1 for e in env.objects if isinstance(e, EliteDrone))
                if num_drones >= MAX_DRONES_ELITE:
                    return

                if self.last_reproduction_time < self.reproduction_cooldown:
                    return

                # Pas assez de santé
                if self.health < self.health_cost + 10:
                    return

                # Probabilité dynamique
                repro_chance = max(0.001, 0.01 * (1 - num_drones / MAX_DRONES_ELITE))
                if random.random() < repro_chance:
                    self._reproduce(env)
                    
                    self.last_reproduction_time = 0
                    self.health -= self.health_cost
                    if self.health <= 0:
                        self.alive = False

    def _reproduce(self, env):
        # Mutation
        new_dna = self.dna.copy()
        trait = random.choice(list(self.DRONE_TRAITS.keys()))
        new_dna[trait] = min(max(
            new_dna[trait] + random.uniform(-0.1, 0.1),
            self.DRONE_TRAITS[trait][0]
        ), self.DRONE_TRAITS[trait][1])
        
        # Héritage des comportements appris (avec légères variations)
        child = EliteDrone(
            x=self.x + random.uniform(-2, 2),
            y=self.y + random.uniform(-2, 2),
            patrol_radius=self.patrol_radius,
            radius=self.radius,
            fire_range=self.fire_range,
            patrol_type=random.choice(["circle", "lemniscate", "random", "square"]),
            role=self.role,
            dna=new_dna
        )
        
        # L'enfant hérite partiellement des stratégies apprises
        for strategy in self.learned_behaviors:
            child.learned_behaviors[strategy] = max(0.1, min(1.0,
                self.learned_behaviors[strategy] + random.uniform(-0.15, 0.15)
            ))
        
        env.spawn_entity(child)