import random
import numpy as np
from collections import deque

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
        
    def push(self, flat_state, minimap, action, reward, flat_next_state, next_minimap, done):
        self.buffer.append((flat_state, minimap, action, reward, flat_next_state, next_minimap, done))

    def sample(self, batch_size):
        samples = random.sample(self.buffer, batch_size)
        flat_s, minimap_s, a, r, flat_s2, minimap_s2, d = zip(*samples)

        return (
            np.array(flat_s),
            np.array(minimap_s),
            np.array(a),
            np.array(r),
            np.array(flat_s2),
            np.array(minimap_s2),
            np.array(d)
        )

    def __len__(self):
        return len(self.buffer)
