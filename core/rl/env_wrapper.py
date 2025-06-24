# core/rl/env_wrapper.py
import os
import numpy as np
from core.agents.agent import Agent
from core.enemys.enemyKamikaze import EnemyKamikaze
from core.entity_types import EntityType
from core.environment import Environment
from core.mini_map import extract_minimap_tensor
from core.objects.energy import EnergySource
from core.objects.explosion import Explosion
from core.objects.quest_item import ObjectiveItem
from core.objects.smoke_zone import JammerZone, SmokeZone
from core.utils import distance_to


class ShooterEnvWrapper:
    def __init__(self, env: Environment, agent):
        self.env = env
        self.agent = agent

    def reset(self):
        self.env.history = [] 
        self.agent = self.env.agents[0]  # à adapter si plusieurs agents
        return self.get_state()

    
    def get_state(self, max_objects=5):
        type_to_index = {
            EntityType.ENERGY_DRONE: 0,
            EntityType.ENERGY_KAMIKAZE: 1,
            EntityType.AGENT: 2,
            EntityType.ENERGY: 3,
            EntityType.TARGET: 4,
            EntityType.DANGER: 5,
            EntityType.JAMMER: 6,
            EntityType.SMOKE: 7,
            EntityType.PROJECTILE: 8,
            EntityType.DECOY: 9,
            EntityType.ENERGY_DRONE_ELITE: 10,
            EntityType.JammerComunication: 11,
            EntityType.WALL: 12
        }
        onehot_size = len(type_to_index)
        object_features = []

        other_agents = [a for a in self.env.agents if a != self.agent and a.alive]
        visible_objects = self.agent.get_vision(self.env.objects + other_agents)

        visible_objects = sorted(visible_objects, key=lambda e: distance_to(self.agent, e))

        for obj in visible_objects[:max_objects]:
            dx = (obj.x - self.agent.x) / self.env.width
            dy = (obj.y - self.agent.y) / self.env.height
            dist = distance_to(self.agent, obj) / max(self.env.width, self.env.height)

            onehot = [0.0] * onehot_size
            etype = getattr(obj, "etype", None)
            if etype in type_to_index:
                onehot[type_to_index[etype]] = 1.0

            # Direction relative (4 bits)
            rel_dir = self.agent.relative_position(obj)
            rel_vector = [
                float(rel_dir["haut_droite"]),
                float(rel_dir["bas_droite"]),
                float(rel_dir["bas_gauche"]),
                float(rel_dir["haut_gauche"]),
            ]

            object_features += [dx, dy, dist] + rel_vector + onehot

        # Padding si on voit moins d'objets
        feature_len = 3 + 4 + onehot_size  # dx, dy, dist + 4 directions + onehot
        while len(object_features) < max_objects * feature_len:
            object_features += [0.0] * feature_len

        agent_info = [
            self.agent.x / self.env.width,
            self.agent.y / self.env.height,
            self.agent.energy / 100.0,
            self.agent.health / 100.0,
            len(self.agent.inbox) / 10.0,
            float(self.agent.alive),
            float(self.agent.zone_interdit)
        ]
        flat_state = np.array(agent_info + object_features, dtype=np.float32)
        minimap_tensor = extract_minimap_tensor(self.agent, self.env,grid_size=64)  # (C, H, W)
        
        return flat_state, minimap_tensor

    
    def step(self, action_idx):
        action = self.agent.action_space[action_idx]
        self.agent.external_action = action

        self.env.step()

        # next_state = self.get_state()
        next_flat, next_minimap = self.get_state()

        # === Récompense ===
        reward = 0.0
        if action['type'] == "attack":
            if self.agent.energy <= 10:
                reward = -0.2

        if getattr(self.agent, "last_attack_success", False):
            reward += 0.1
            self.agent.last_attack_success = False

        if self.agent.alive:
            reward += 0.05  # Survie

            # Repérage d’ennemis
            enemies = [o for o in self.env.objects if o.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE,EntityType.TARGET,EntityType.ENEMY_TURREL]]
            visible = self.agent.get_vision(enemies)
            if visible:
                reward += 0.5
            
            for o in visible:
                if o.etype in [EntityType.ENERGY_DRONE, EntityType.ENERGY_KAMIKAZE,EntityType.ENEMY_TURREL]:
                    dist = distance_to(self.agent, o)
                    if dist > 15:
                        reward += 0.2

            # Exploration (centré sur la map)
            dist = np.linalg.norm(np.array([self.agent.x, self.agent.y]) - np.array([self.env.width/2, self.env.height/2]))
            reward += (1 - dist / max(self.env.width, self.env.height)) * 0.1

            # Objectif proche
            near_objective = any(
                isinstance(o, ObjectiveItem) and distance_to(self.agent, o) < 5.0
                for o in self.env.objects
            )
            if near_objective:
                reward += 1.0

            # Énergie proche
            near_energy = any(
                isinstance(o, EnergySource) and distance_to(self.agent, o) < o.radius+0.5
                for o in self.env.objects
            )
            if near_energy :#and self.agent.energy < 100:
                reward += 0.05

            # Longévité
            if hasattr(self.agent, "time_alive") and self.agent.time_alive > 300:
                reward += 0.3

            # Pénalité d'inaction (facultatif)
            if self.agent.energy > 90 and len(visible) == 0:
                reward -= 0.4

        else:
            reward -= 1.5  # Mort
        if self.agent.zone_interdit:
            reward -= 0.4
            
        done = not self.agent.alive
        return next_flat, next_minimap, reward, done
