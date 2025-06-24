import json
from typing import Dict
from core.enemys.decoy import Decoy
from core.entity import Entity
from core.objects.explosion import Explosion
from core.objects.smoke_zone import  JammerCommunication, JammerZone, SmokeZone
from core.scene_objects import spawn_agent, spawn_objects
from core.utils import to_serializable
from core.vision import Vision
from core.objects.projectile import Projectile


class Environment:
    def __init__(self, width=500, height=500, use_rl=False):
        self.width = width
        self.height = height
        self.use_rl=use_rl
        
        self.agents =self._spawn_agent()
        self.vision = Vision()
        self.objects = self._spawn_objects()
        self.history = []
        
        
        self.time =0
        
        
        

    def _spawn_objects(self):
        return spawn_objects()
        
    def _spawn_agent(self):
        return spawn_agent(self.use_rl)

        
    def spawn_explosion(self, x, y, radius=3.0):
        explosion = Explosion(x, y, radius)
        self.objects.append(explosion)
        
    def spawn_projectile(self, x, y, dx, dy,owner=None):
        proj = Projectile(x, y, dx, dy,owner)
        self.objects.append(proj)
        
   
    def spawn_jammer_communication(self, x, y,moving, owner=None):
        jammer = JammerCommunication(x, y,radius=20.0,moving=moving,ttl=10)
        self.objects.append(jammer)
        
    def spawn_smoke_zone(self, x, y,moving, owner=None):
        smoke = SmokeZone(x, y,radius=20.0,moving=moving,ttl=10)
        self.objects.append(smoke)
        
    def spawn_jammer(self, x, y,moving, owner=None):
        jammerZone = JammerZone(x, y,radius=20.0,moving=moving,ttl=10)
        self.objects.append(jammerZone)
        
    def spawn_entity(self,child):
        self.objects.append(child)
        
    def spawn_decoy(self, x, y, lifespan=20):
        decoy = Decoy(x, y, lifespan)
        self.objects.append(decoy)



    def step(self):
        self.time +=1
        all_messages = []
        for agent in self.agents:
            agent.env = self  # Injecter le contexte s'il n'est pas déjà dedans
            msgs = agent.send_message()
            all_messages.extend(msgs)

        # Étape 2 : Redistribuer les messages
        for agent in self.agents:
            agent.receive_messages(all_messages)
            agent.reset_step_flags()  #mise a jour des flags ici avant les methode update()
            
      
            
        # Mettre à jour les objets (mines, drones, etc.)
        for obj in self.objects:
            if hasattr(obj, 'update'):
                obj.update(self)

        step_info = []

        # Boucle d'action des agents
        for agent in self.agents:
            if not agent.alive:
                continue
            # if agent.last_attack_success==True:
            #     print("toucher un objet agent ",agent.last_attack_success)
            # Perception de l'agent
            visible = self.vision.get_visible(agent, self.objects)#on peu ajouter autre infos d'observation comme les echange de message
 
            # S’il y a une action RL injectée, on l’utilise
            if hasattr(agent, "external_action") and agent.external_action is not None:
                action = agent.external_action
                agent.external_action = None
            else:
                action = agent.decide_action(visible)
            agent.perform_action(action, self)
            visible = self.objects
           
           
            step_info.append({
                'agent': agent.to_dict(),
                'facing': agent.get_orientation(),
                'action': action,
                'visible': [o.to_dict() for o in visible if getattr(o, "alive", True)]
            })

        # Nettoyer les objets morts
        self.objects = [o for o in self.objects if getattr(o, "alive", True)]
        self.agents = [a for a in self.agents if a.alive]

        #print(len(self.objects))
     
        self.history.append(step_info)
        #print(f"[STEP] Frame {self.time} — total history size: {len(self.history)}")


    def run(self, steps=100):
        for _ in range(steps):
            self.step()

    def export(self, path="data/output.json"): 
        with open(path, "w") as f:
            json.dump(to_serializable(self.history), f, indent=2)
    
    
    
