from core.rl.models.dqn_model import DQN
from core.rl.replay_buffer import ReplayBuffer

import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim
import torch.nn.functional as F

class DQNTrainer:
    def __init__(self, state_dim, action_dim, device='cpu'):
        self.device = torch.device(device)

        self.q_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net = DQN(state_dim, action_dim).to(self.device)
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

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            action= np.random.randint(0, self.action_dim)
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                action= self.q_net(state_tensor).argmax().item()
            
        # Décroissance de l’epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        return action

    def train_step(self):
        if len(self.replay_buffer) < self.batch_size:
            return  # Pas assez d'échantillons pour apprendre

        # Sample du buffer
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        

        # Conversion tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        # Q(s,a)
        q_values = self.q_net(states).gather(1, actions)

        # Double DQN : choisir a' avec q_net, évaluer avec target_net
        with torch.no_grad():
            next_actions = self.q_net(next_states).argmax(1, keepdim=True)
            next_q_values = self.target_net(next_states).gather(1, next_actions)
            target_q = rewards + self.gamma * next_q_values * (1 - dones)

        # Huber loss (plus stable que MSE)
        loss = F.smooth_l1_loss(q_values, target_q)

        # Optimisation
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.q_net.parameters(), max_norm=1.0)
        self.optimizer.step()

    def update_target(self):
        """ Met à jour le réseau cible avec les poids du réseau principal """
        self.target_net.load_state_dict(self.q_net.state_dict())
