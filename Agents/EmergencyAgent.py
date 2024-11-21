from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import random


class EmergencyAgent(Agent):
    def __init__(self, jid, password, building):
        super().__init__(jid, password)
        self.building = building  # Referência ao edifício
        self.emergency_type = None
        self.hacked_systems = []  # Rastreamento de sistemas afetados por ataques informáticos

    class EmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            """Gerencia emergências e condições dinâmicas."""
            await asyncio.sleep(5)  # Atraso para permitir inicialização
            if not self.agent.emergency_type:
                # Inicia uma emergência
                self.agent.emergency_type = self.agent.start_emergency()
                print(f"Emergency initiated: {self.agent.emergency_type}")

            # Atualiza condições de emergência dinâmicas
            rn = random.random()
            if rn < 0.01:
                self.agent.start_fire()
            elif rn < 0.02:
                self.agent.update_informatic_attack()
            elif rn < 0.03:
                self.agent.start_earthquake()

    def start_emergency(self):
        """Inicia uma emergência selecionando um tipo aleatório."""
        emergencies = {
            "Fire": 0.35,
            "Earthquake": 0.25,
            "Gas Leak": 0.2,
            "Security Threat": 0.1,
            "Informatic Attack": 0.1,
        }
        self.emergency_type = random.choices(list(emergencies.keys()), weights=emergencies.values(), k=1)[0]
        self.send_emergency_to_bms(self.emergency_type)

        if self.emergency_type == "Fire":
            self.start_fire()
        elif self.emergency_type == "Earthquake":
            self.start_earthquake()
        elif self.emergency_type == "Gas Leak":
            pass  # Apenas evacuar
        elif self.emergency_type == "Security Threat":
            self.start_security_threat()
        elif self.emergency_type == "Informatic Attack":
            self.start_informatic_attack()
        return self.emergency_type

    def send_emergency_to_bms(self, emergency_type, fire_room=None, earthquake_room=None, security_room=None):
        """
        Envia uma mensagem ao BMSAgent com o tipo de emergência.
        Para incêndios, inclui as coordenadas da sala em chamas.
        """
        msg = Message(to="bms@localhost")  # Envia diretamente ao BMSAgent
        if emergency_type == "Fire" and fire_room:
            # Inclui as coordenadas da sala no caso de incêndio
            msg.body = f"Emergency:{emergency_type},Location:{fire_room.row},{fire_room.col},{fire_room.floor}"
            print(f"EmergencyAgent: Mensagem enviada ao BMSAgent sobre incêndio na sala ({fire_room.row}, {fire_room.col}, Floor {fire_room.floor}).")
        elif emergency_type == "Earthquake" and earthquake_room:
            # Inclui as coordenadas da sala no caso de incêndio
            msg.body = f"Emergency:{emergency_type},Location:{earthquake_room.row},{earthquake_room.col},{earthquake_room.floor}"
            print(f"EmergencyAgent: Mensagem enviada ao BMSAgent sobre terremoto na sala ({earthquake_room.row}, {earthquake_room.col}, Floor {earthquake_room.floor}).")
        elif emergency_type == "Security Threat" and security_room:
            # Inclui as coordenadas da sala no caso de incêndio
            msg.body = f"Emergency:{emergency_type},Location:{security_room.row},{security_room.col},{security_room.floor}"
            print(f"EmergencyAgent: Mensagem enviada ao BMSAgent sobre ameaça de segurança na sala ({security_room.row}, {security_room.col}, Floor {security_room.floor}).")
        else:
            msg.body = f"Emergency:{emergency_type}"
            print(f"EmergencyAgent: Mensagem enviada ao BMSAgent sobre emergência: {emergency_type}.")
        
        asyncio.create_task(self.send(msg))

    def start_informatic_attack(self):
        """Inicia um ataque informático em sistemas aleatórios do edifício."""
        systems = ["doors", "communication", "elevators"]
        self.hacked_systems = random.sample(systems, k=random.randint(1, len(systems)))
        self.send_emergency_to_bms("Informatic Attack")
        for system in self.hacked_systems:
            if system == "doors":
                self.building.lock_doors = True
            elif system == "elevators":
                self.building.lock_elevators = True
            elif system == "communication":
                self.building.lock_communications = True
        print(f"Informatic attack targets: {self.hacked_systems}")

    def update_informatic_attack(self):
        """Simula efeitos contínuos de ataques informáticos."""
        rn = random.random()
        if rn < 0.33:
            self.building.lock_doors = True
        elif rn < 0.66:
            self.building.lock_communications = True
        else:
            self.building.lock_elevators = True

    def start_fire(self):
        """Inicia um incêndio utilizando métodos do `building.py`."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            fire_room = random.choice(unoccupied_rooms)
            fire_room.fires()  # Chama o método do building.py
            self.send_emergency_to_bms("Fire", fire_room)
            print(f"Fire started in room ({fire_room.row}, {fire_room.col}, Floor {fire_room.floor})")

    def start_earthquake(self):
        """Simula um terremoto utilizando métodos do `building.py`."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            earthquake_room = random.choice(unoccupied_rooms)
            earthquake_room.earthquake()  # Chama o método do building.py
            self.send_emergency_to_bms("Earthquake", earthquake_room)
        print("Earthquake damage applied to all rooms.")

    def start_security_threat(self):
        """Simula uma ameaça de segurança em áreas específicas."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            security_room = random.choice(unoccupied_rooms)
            security_room.security_threath()
            self.send_emergency_to_bms("Security Threat", security_room)
            print("Security threat initiated.")

    def get_unoccupied_rooms(self, room_type=None):
        """
        Obtém uma lista de salas desocupadas de um tipo específico (e.g., "H").
        Exclui salas marcadas como ocupadas.
        """
        return [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and not room.is_occupied and (room_type is None or room.room_type == room_type)
        ]

    async def setup(self):
        """Configura o EmergencyBehaviour para o agente."""
        print("EmergencyAgent started.")
        self.add_behaviour(self.EmergencyBehaviour())
