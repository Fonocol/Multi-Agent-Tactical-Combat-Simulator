import random
import numpy as np
from collections import deque

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, s, a, r, s2, d):
        self.buffer.append((s, a, r, s2, d))

    def sample(self, batch_size):
        samples = random.sample(self.buffer, batch_size)
        s, a, r, s2, d = zip(*samples)
        return np.array(s), a, r, np.array(s2), d

    def __len__(self):
        return len(self.buffer)
