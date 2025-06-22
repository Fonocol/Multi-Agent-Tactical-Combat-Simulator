# main.py
import json
from core.environment import Environment
from core.rl.env_wrapper import ShooterEnvWrapper
from core.rl.q_learning import QLearningAgent
import sys

def run_simulation():
    env = Environment()
    env.run(steps=1000)
    env.export(path="viewer/data/output.json")
    print("✅ Simulation terminée : fichier exporté dans data/output.json")
  
def train_rl():
    rl_agent = QLearningAgent(n_states=5, n_actions=9)
    episodes_to_export = 10  # Épisodes à exporter
    
    # Liste des épisodes disponibles pour l'interface
    available_episodes = []
    
    for episode in range(20):
        env = Environment(use_rl=True)
        wrapper = ShooterEnvWrapper(env, env.agents[0])
        state = wrapper.reset()
        
        for _ in range(20):
            action = rl_agent.select_action(state)
            next_state, reward, done = wrapper.step(action)
            rl_agent.update(state, action, reward, next_state)
            state = next_state
            
            if done:
                break

        print(f"Épisode {episode + 1} terminé.")

        # Sauvegarde les épisodes intéressants
        if (episode + 1)%episodes_to_export==0:
            episode_id = f"episode_{episode + 1}"
            env.export(path=f"viewer/data/{episode_id}.json")
            available_episodes.append({
                "id": episode_id,
                "name": f"Episode {episode + 1} - {'Entrainement' if episode + 1 < 300 else 'Combat'}"
            })
            print(f"Épisode {episode + 1} exporté.")
    
    # Sauvegarde la liste des épisodes disponibles
    with open("viewer/data/available_episodes.json", "w") as f:
        json.dump(available_episodes, f)
    
    print("🏁 Entraînement RL terminé.")

def train_dqn():

    from core.rl.trainers.train_dqn import DQNTrainer
    from core.rl.env_wrapper import ShooterEnvWrapper
    from core.environment import Environment

    trainer = DQNTrainer(state_dim=20*5+6, action_dim=13)
    episodes_to_export = 20  # Épisodes à exporter
    
    # Liste des épisodes disponibles pour l'interface
    available_episodes = []

    for episode in range(500):
        env = Environment(use_rl=True)
        wrapper = ShooterEnvWrapper(env, env.agents[0])
        state = wrapper.reset()

        for _ in range(10000):
            
            action = trainer.select_action(state)
            next_state, reward, done = wrapper.step(action)
            trainer.replay_buffer.push(state, action, reward, next_state, done)
            trainer.train_step()
            state = next_state
            if done:
                break
            
        print(f"✅ Episode {episode + 1} done")
        # Sauvegarde les épisodes intéressants
        if (episode + 1)%episodes_to_export==0:
            episode_id = f"episode_{episode + 1}"
            env.export(path=f"viewer/data/{episode_id}.json")
            available_episodes.append({
                "id": episode_id,
                "name": f"Episode {episode + 1} - {'Entrainement' if episode + 1 < 5000 else 'Combat'}"
            })
            print(f"Épisode {episode + 1} exporté.")
    
    # Sauvegarde la liste des épisodes disponibles
    with open("viewer/data/available_episodes.json", "w") as f:
        json.dump(available_episodes, f)
    
    print("🏁 Entraînement DQN terminé.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "simulation"

    if mode == "simulation":
        run_simulation()
    elif mode == "train_rl":
        train_rl()
    elif mode == "train_dqn":
        train_dqn()
    else:
        print("❌ Mode inconnu. Utilise 'simulation' ou 'train_rl'")
