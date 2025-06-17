from core.entity import Entity
from core.entity_types import EntityType

class CommandCenterAgent(Entity):
    def __init__(self, x, y, radius=1.0):
        super().__init__(x, y, radius=radius, etype=EntityType.COMMAND_CENTER)
        self.inbox = []
        self.last_action = None

    def get_observation(self, env):
        messages = env.collect_all_messages()
        agent_states = [(a.x, a.y, a.health) for a in env.agents]
        enemies_spotted = sum(1 for m in messages if m["type"] == "enemy_spotted")
        obs = {
            "messages": messages,
            "nb_agents_alive": sum(1 for a in env.agents if a.alive),
            "nb_enemies_detected": enemies_spotted,
            "agent_states": agent_states
        }
        return obs

    def decide_action(self, observation):
        # Placeholder: à remplacer par une policy RL
        if observation["nb_enemies_detected"] > 3:
            action = 1  # relayer tous les messages
        else:
            action = 0  # ne rien faire
        self.last_action = action
        return action

    def perform_action(self, action, env):
        if action == 0:
            return
        elif action == 1:
            for agent in env.agents:
                agent.inbox.extend(self.inbox)
        elif action == 2:
            # filtrer les messages douteux
            safe = [m for m in self.inbox if "enemy" in m["type"]]
            for agent in env.agents:
                agent.inbox.extend(safe)
        elif action == 3:
            self.inbox = []
        elif action == 4:
            fake_msg = {"type": "enemy_spotted", "pos": (20, 20), "sender": "CC_FAKE"}
            for agent in env.agents:
                agent.inbox.append(fake_msg)
