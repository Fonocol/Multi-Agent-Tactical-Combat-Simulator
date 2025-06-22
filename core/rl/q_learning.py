# core/rl/q_learning.py
import numpy as np

class QLearningAgent:
    def __init__(self, n_states, n_actions, alpha=0.1, gamma=0.95, epsilon=0.1):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.n_actions = n_actions

    def get_qs(self, state):
        key = tuple(np.round(state, 2))
        if key not in self.q_table:
            self.q_table[key] = np.zeros(self.n_actions)
        return self.q_table[key]

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_actions)
        return np.argmax(self.get_qs(state))

    def update(self, state, action, reward, next_state):
        key = tuple(np.round(state, 2))
        next_qs = self.get_qs(next_state)
        target = reward + self.gamma * np.max(next_qs)
        self.q_table[key][action] += self.alpha * (target - self.q_table[key][action])
        
        