from core.environment import Environment

if __name__ == "__main__":
    env = Environment()
    env.run(steps=100)
    env.export(path="viewer/data/output.json") #verification execution etant dans le bon directory
    print("✅ Simulation terminée : fichier exporté dans data/output.json")
