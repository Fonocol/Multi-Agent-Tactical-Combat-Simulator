from core.environment import Environment

if __name__ == "__main__":
    env = Environment()
    env.run(steps=5)
    env.export()
    print("✅ Simulation terminée : fichier exporté dans data/output.json")
