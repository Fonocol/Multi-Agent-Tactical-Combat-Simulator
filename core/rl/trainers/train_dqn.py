from core.rl.models.dqn_model import DQN, CombinedDQN
from core.rl.replay_buffer import ReplayBuffer

import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim
import torch.nn.functional as F

class DQNTrainer:
    def __init__(self, state_dim, action_dim, device='cpu'):
        self.device = torch.device(device)
        self.q_net = CombinedDQN(flat_input_dim=state_dim, output_dim=action_dim).to(self.device)
        self.target_net = CombinedDQN(flat_input_dim=state_dim, output_dim=action_dim).to(self.device)

        # self.q_net = DQN(state_dim, action_dim).to(self.device)
        # self.target_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=1e-3)
        self.replay_buffer = ReplayBuffer(capacity=10000)
        self.batch_size = 64
        self.gamma = 0.99

        # Exploration params
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        
        self.action_dim =action_dim

    # def select_action(self, state):
    #     if np.random.rand() < self.epsilon:
    #         action= np.random.randint(0, self.action_dim)
    #     else:
    #         state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
    #         with torch.no_grad():
    #             action= self.q_net(state_tensor).argmax().item()
            
    #     # Décroissance de l’epsilon
    #     self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    #     return action
    
    def select_action(self, flat_state, minimap_tensor):
        flat_state_tensor = torch.FloatTensor(flat_state).unsqueeze(0).to(self.device)
        minimap_tensor = torch.FloatTensor(minimap_tensor).unsqueeze(0).to(self.device)  # (1, C, H, W)

        if np.random.rand() < self.epsilon:
            action = np.random.randint(0, self.action_dim)
        else:
            with torch.no_grad():
                q_values = self.q_net(flat_state_tensor, minimap_tensor)
                action = q_values.argmax().item()

        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return action


    def train_step(self):
        if len(self.replay_buffer) < self.batch_size:
            return  # Pas assez d'échantillons

        # === Sample ===
        flat_states, minimaps, actions, rewards, flat_next_states, next_minimaps, dones = self.replay_buffer.sample(self.batch_size)

        # === Conversion en tensors ===
        flat_states = torch.FloatTensor(flat_states).to(self.device)
        minimaps = torch.FloatTensor(minimaps).to(self.device)

        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        flat_next_states = torch.FloatTensor(flat_next_states).to(self.device)
        next_minimaps = torch.FloatTensor(next_minimaps).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        # === Q(s, a) ===
        q_values = self.q_net(flat_states, minimaps).gather(1, actions)

        # === Double DQN ===
        with torch.no_grad():
            next_actions = self.q_net(flat_next_states, next_minimaps).argmax(1, keepdim=True)
            next_q_values = self.target_net(flat_next_states, next_minimaps).gather(1, next_actions)
            target_q = rewards + self.gamma * next_q_values * (1 - dones)

        # === Perte et descente de gradient ===
        loss = F.smooth_l1_loss(q_values, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.q_net.parameters(), max_norm=1.0)
        self.optimizer.step()

    
    def update_target(self):
        """ Met à jour le réseau cible avec les poids du réseau principal """
        self.target_net.load_state_dict(self.q_net.state_dict())
