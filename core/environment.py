import json
from core.objects.explosion import Explosion
from core.objects.smoke_zone import  JammerCommunication, SmokeZone
from core.scene_objects import spawn_agent, spawn_objects
from core.vision import Vision
from core.objects.projectile import Projectile


class Environment:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.agents =self._spawn_agent()
        self.vision = Vision()
        self.objects = self._spawn_objects()
        self.history = []

    def _spawn_objects(self):
        return spawn_objects()
        
    def _spawn_agent(self):
        return spawn_agent()

        
    def spawn_explosion(self, x, y, radius=3.0):
        explosion = Explosion(x, y, radius)
        self.objects.append(explosion)
        
    def spawn_projectile(self, x, y, dx, dy,owner=None):
        proj = Projectile(x, y, dx, dy,owner)
        self.objects.append(proj)
        
   
    def spawn_jammer_communication(self, x, y, owner=None):
        jammer = JammerCommunication(x, y,radius=6.0)
        self.objects.append(jammer)
        
    def spawn_smoke_zone(self, x, y,moving, owner=None):
        smoke = SmokeZone(x, y,radius=5.0,moving=moving)
        self.objects.append(smoke)



    def step(self):
        all_messages = []
        for agent in self.agents:
            agent.env = self  # Injecter le contexte s'il n'est pas déjà dedans
            msgs = agent.send_message()
            all_messages.extend(msgs)

        # Étape 2 : Redistribuer les messages
        for agent in self.agents:
            agent.receive_messages(all_messages)
            
      
            
        # Mettre à jour les objets (mines, drones, etc.)
        for obj in self.objects:
            if hasattr(obj, 'update'):
                obj.update(self)

        step_info = []

        # Boucle d'action des agents
        for agent in self.agents:
            if not agent.alive:
                continue

            #
            # Perception de l'agent
            visible = self.vision.get_visible(agent, self.objects)#on peu ajouter autre infos d'observation comme les echange de message
            action = agent.decide_action(visible)
            agent.perform_action(action, self)
            visible = self.objects
           

            step_info.append({
                'agent': agent.to_dict(),
                'facing': agent.get_orientation(),
                'visible': [o.to_dict() for o in visible if getattr(o, "alive", True)]
            })

        # Nettoyer les objets morts
        self.objects = [o for o in self.objects if getattr(o, "alive", True)]
        self.agents = [a for a in self.agents if a.alive]

        self.history.append(step_info)


    def run(self, steps=100):
        for _ in range(steps):
            self.step()

    def export(self, path="data/output.json"): 
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)
            
        with open('data/output.json', "w") as f:
            json.dump(self.history, f, indent=2)


