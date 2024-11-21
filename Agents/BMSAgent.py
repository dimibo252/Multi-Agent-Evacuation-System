from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from building import Building


class BMSAgent(Agent):
    def __init__(self, jid, password, num_occupants, role, building: Building):
        super().__init__(jid, password)
        self.building = building
        self.num_occupants = num_occupants  # Número de ocupantes a serem notificados
        self.elevator_locked = False

    class ReceiveEmergencyMessages(CyclicBehaviour):
        async def run(self):
            """Recebe mensagens do EmergencyAgent e age conforme necessário."""
            message = await self.receive(timeout=1)  # Aguarda mensagens
            if message:
                if "Emergency:" in message.body:
                    # Processa o tipo de emergência e a localização
                    emergency_data = message.body.split(",")
                    emergency_type = emergency_data[0].split(":")[1]
                    print(f"BMSAgent: Emergency received: {emergency_type}")
                    location = None
                    if len(emergency_data) > 1:
                        location_data = emergency_data[1].split(":")[1].split(",")
                        location = {
                            "row": int(location_data[0]),
                            "col": int(location_data[1]),
                            "floor": int(location_data[2]),
                        }
                        print(f"BMSAgent: Location received: {location}")

                    await self.agent.handle_emergency(emergency_type, location)

    async def handle_emergency(self, emergency_type, location=None):
        """Lida com emergências recebidas."""
        if emergency_type == "Fire":
            print("BMSAgent: Managing Fire.")
            await self.lock_elevator()
            fire_message = f"Fire detected. Evacuate immediately. Location: {location}" if location else "Fire detected. Evacuate immediately."
            await self.notify_all_occupants(fire_message)
            # Notifica o fireman
            fireman_jid = "fireman@localhost"
            fireman_message = Message(to=fireman_jid)
            fireman_message.body = f"Emergency:{emergency_type},Location:{location['row']},{location['col']},{location['floor']}"
            await self.send(fireman_message)
            print(f"BMSAgent: Message sent to the fireman: {fireman_message.body}")

        elif emergency_type == "Earthquake":
            print("BMSAgent: Managing Earthquake.")
            earthquake_message = f"Earthquake detected. Evacuate immediately. Location: {location}" if location else "Earthquake detected. Evacuate immediately."
            await self.notify_all_occupants(earthquake_message)
            # Notifica o responsável por terremotos
            earthquake_responder_jid = "earthquake_responder@localhost"
            responder_message = Message(to=earthquake_responder_jid)
            responder_message.body = f"Emergency:{emergency_type},Location:{location['row']},{location['col']},{location['floor']}"
            await self.send(responder_message)
            print(f"BMSAgent: Message Sent to the earthquakes responsible: {responder_message.body}")

        elif emergency_type == "Gas Leak":
            print("BMSAgent: Managing Gas Leak.")
            await self.lock_elevator()
            gas_message = "Gas leak detected. Evacuate immediately."
            await self.notify_all_occupants(gas_message)
            # Notifica o responsável por vazamentos de gás
            gas_responder_jid = "gas_responder@localhost"
            responder_message = Message(to=gas_responder_jid)
            responder_message.body = f"Emergency:{emergency_type}"
            await self.send(responder_message)
            print(f"BMSAgent: Message sent to the gas leaks responsible: {responder_message.body}")

        elif emergency_type == "Security Threat":
            print("BMSAgent: Managing security threat.")
            security_message = f"Security threat detected. Evacuate immediately. Location: {location}" if location else "Security threat detected. Evacuate immediately."
            await self.notify_all_occupants(security_message)
            # Notifica o responsável por segurança
            security_responder_jid = "cop@localhost"
            responder_message = Message(to=security_responder_jid)
            responder_message.body = f"Emergency:{emergency_type},Location:{location['row']},{location['col']},{location['floor']}"
            await self.send(responder_message)
            print(f"BMSAgent: Message sent to the security responsible: {responder_message.body}")

        elif emergency_type == "Informatic Attack":
            print("BMSAgent: Managing informatic attack.")
            informatic_message = "Informatic attack ongoing. Systems compromised."
            await self.notify_all_occupants(informatic_message)
            # Notifica o responsável por ataques informáticos
            informatic_responder_jid = "it_responder@localhost"
            responder_message = Message(to=informatic_responder_jid)
            responder_message.body = f"Emergency:{emergency_type}"
            await self.send(responder_message)
            print(f"BMSAgent: Message sent to the IT responsible: {responder_message.body}")

    async def lock_elevator(self):
        """Tranca os elevadores."""
        if not self.elevator_locked:
            self.elevator_locked = True
            print("BMSAgent: Elevators blocked due to emergency.")

    async def unlock_elevator(self):
        """Destranca os elevadores."""
        if self.elevator_locked:
            self.elevator_locked = False
            print("BMSAgent: Elevators Unlocked.")

    async def notify_all_occupants(self, message_body):
        """Envia notificações para os ocupantes."""
        print(f"BMSAgent: Notifying occupants: {message_body}")
        for i in range(1, self.num_occupants + 1):
            occupant_jid = f"occupant{i}@localhost"
            occupant_message = Message(to=occupant_jid)
            occupant_message.body = message_body
            await self.send(occupant_message)
            print(f"BMSAgent: Message sent to {occupant_jid}")

    async def setup(self):
        """Configura os comportamentos do BMSAgent."""
        print("BMSAgent started...")
        self.add_behaviour(self.ReceiveEmergencyMessages())
