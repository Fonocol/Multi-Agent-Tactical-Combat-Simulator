# Multi-Agent Tactical Combat Simulator

## 🎯 Objectif

Ce projet simule un environnement de **combat multi-agent 2D** dans lequel plusieurs agents interagissent avec des ennemis, obstacles et ressources, tout en prenant des décisions individuelles basées sur leur propre perception du terrain.

C’est une base modulaire pour :

- Prototyper des comportements d’agents (aléatoires, scriptés ou RL)
- Expérimenter avec la vision, la communication, et les tactiques de groupe
- Entraîner des agents intelligents via **apprentissage par renforcement multi-agent (MARL)** à terme

---

## 🛠️ Fonctionnalités

- Environnement de combat 2D (carte, murs, ennemis, ressources)
- Agents dotés d’un **champ de vision** (FOV, portée, angle)
- Agents spéciaux : **Support (soignant), Scout, Heavy, Sniper**, etc.
- Attaques, déplacements, collisions et gestion de la santé
- Système de **perception locale** et de **décisions autonomes**
- Génération de logs `.json` utilisables pour visualisation
- Visualiseur JS via Canvas (`output.json` → rendu dynamique)

---

## 🖼️ Visualisation

Une interface JS simple permet de **jouer les frames** du fichier `output.json` pour observer les perceptions et décisions de chaque agent à chaque étape.

---

## 🧩 À venir

- Ajout de **communication inter-agents**
- Intégration de modèles **Reinforcement Learning**
- Apprentissage de stratégies collectives et spécialisées
- Entraînements dans différents scénarios

---

---

## 💡 Technologies utilisées

- Python (simulation)
- HTML/JS (visualisation)
- JSON (export des frames)

---

## ⚙️ Installation et Lancement

### 1. Cloner le projet

```bash
git clone https://github.com/Fonocol/Multi-Agent-Tactical-Combat-Simulator.git
cd Multi-Agent-Tactical-Combat-Simulator
```

### 2.Exécuter la simulation (Python)

Assure-toi d’avoir Python 3.8+ :

```
python main.py
```

Cela génère un fichier data/output.json

### 3. Visualiser la simulation (HTML / JS)

Ouvre un terminal et lance un serveur local dans le dossier `viewer`

```bash
cd viewer
python -m http.server 8000
```

Ensuite, ouvre ton navigateur à l’adresse :

```bash
http://localhost:8000
```

Tu verras la simulation animée dans le canvas `simCanvas`

## Aperçu de la simulation

![Simulation combat](/viewer/assets/view.png)

## 🤝 Contribution

Les PR sont les bienvenues ! L’objectif est de créer une plateforme flexible pour tester des idées en **IA distribuée**, **stratégies de combat**, et **apprentissage multi-agent**.

---

## 📜 Licence

Ce projet est open-source et sous licence MIT.

```

```
