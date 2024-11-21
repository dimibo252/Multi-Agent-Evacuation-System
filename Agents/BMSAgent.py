from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
import asyncio
from building import Building


class BMSAgent(Agent):
    def __init__(self, jid, password, num_occupants, role, building: Building):
        super().__init__(jid, password)
        self.building = building
        self.num_occupants = num_occupants  # Number of occupants to be notified
        self.emergency_type = None
        self.location = None

    class ReceiveEmergencyMessages(CyclicBehaviour):
        async def run(self):
            """Receives messages from EmergencyAgent and processes them."""
            message = await self.receive(timeout=1)  # Wait for messages
            if message and "Emergency:" in message.body:
                # Process the emergency type and location
                emergency_data = message.body.split(",")
                self.agent.emergency_type = emergency_data[0].split(":")[1]
                print(f"BMSAgent: Received emergency: {self.agent.emergency_type}")
                
                self.agent.location = None
                if len(emergency_data) > 1:
                    location_data = emergency_data[1].split(":")[1].split(",")
                    self.agent.location = {
                        "row": int(location_data[0]),
                        "col": int(location_data[1]),
                        "floor": int(location_data[2]),
                    }
                    print(f"BMSAgent: Location received: {self.agent.location}")
                
                # Trigger the behavior to handle the emergency
                self.agent.add_behaviour(self.agent.HandleEmergency())

    class NotifyOccupants(OneShotBehaviour):
        def __init__(self, message_body):
            super().__init__()
            self.message_body = message_body

        async def run(self):
            """Notifies all occupants about the emergency."""
            print(f"BMSAgent: Notifying occupants: {self.message_body}")
            for i in range(1, self.agent.num_occupants + 1):
                occupant_jid = f"occupant{i}@localhost"
                occupant_message = Message(to=occupant_jid)
                occupant_message.body = self.message_body
                await self.send(occupant_message)
                print(f"BMSAgent: Message sent to {occupant_jid}")

    class NotifyResponder(OneShotBehaviour):
        def __init__(self, responder_jid, responder_message):
            super().__init__()
            self.responder_jid = responder_jid
            self.responder_message = responder_message

        async def run(self):
            """Sends a message to the relevant responder."""
            message = Message(to=self.responder_jid)
            message.body = self.responder_message
            await self.send(message)
            print(f"BMSAgent: Message sent to {self.responder_jid}: {message.body}")

    class HandleEmergency(OneShotBehaviour):
        async def run(self):
            """Handles the current emergency."""
            emergency_type = self.agent.emergency_type
            location=self.agent.location

            if emergency_type == "Fire":
                print("BMSAgent: Managing fire.")
                await self.agent.unlock_doors()
                await self.agent.lock_elevator()
                fire_message = (
                    f"Fire detected. Evacuate immediately. Location: {location}" 
                    if location 
                    else "Fire detected. Evacuate immediately."
                )
                self.agent.add_behaviour(self.agent.NotifyOccupants(fire_message))
                fireman_jid = "fireman@localhost"
                fireman_message = f"Emergency:{emergency_type},Location:{location['row']},{location['col']},{location['floor']}"
                self.agent.add_behaviour(self.agent.NotifyResponder(fireman_jid, fireman_message))

            elif emergency_type == "Earthquake":
                print("BMSAgent: Managing earthquake.")
                await self.agent.unlock_doors()
                await self.agent.lock_elevator()
                earthquake_message = (
                    f"Earthquake detected. Evacuate immediately. Location: {location}" 
                    if location 
                    else "Earthquake detected. Evacuate immediately."
                )
                self.agent.add_behaviour(self.agent.NotifyOccupants(earthquake_message))
                responder_jid = "earthquake_responder@localhost"
                responder_message = f"Emergency:{emergency_type},Location:{location['row']},{location['col']},{location['floor']}"
                self.agent.add_behaviour(self.agent.NotifyResponder(responder_jid, responder_message))

            elif emergency_type == "Gas Leak":
                print("BMSAgent: Managing gas leak.")
                await self.agent.unlock_doors()
                gas_message = "Gas leak detected. Evacuate immediately."
                self.agent.add_behaviour(self.agent.NotifyOccupants(gas_message))
                responder_jid = "gas_responder@localhost"
                responder_message = f"Emergency:{emergency_type}"
                self.agent.add_behaviour(self.agent.NotifyResponder(responder_jid, responder_message))

            elif emergency_type == "Security Threat":
                print("BMSAgent: Managing security threat.")
                await self.agent.unlock_doors()
                security_message = (
                    f"Security threat detected. Evacuate immediately. Location: {location}" 
                    if location 
                    else "Security threat detected. Evacuate immediately."
                )
                self.agent.add_behaviour(self.agent.NotifyOccupants(security_message))
                responder_jid = "cop@localhost"
                responder_message = f"Emergency:{emergency_type},Location:{location['row']},{location['col']},{location['floor']}"
                self.agent.add_behaviour(self.agent.NotifyResponder(responder_jid, responder_message))

            elif emergency_type == "Informatic Attack":
                await self.agent.unlock_doors()
                await self.agent.lock_elevator()
                print("BMSAgent: Managing informatic attack.")
                informatic_message = "Informatic attack ongoing. Systems compromised."
                self.agent.add_behaviour(self.agent.NotifyOccupants(informatic_message))
                responder_jid = "it_responder@localhost"
                responder_message = f"Emergency:{emergency_type}"
                self.agent.add_behaviour(self.agent.NotifyResponder(responder_jid, responder_message))

    async def lock_elevator(self):
        """Locks the elevators."""
        self.building.lock_elevators=True
        print("BMSAgent: Elevators locked due to emergency.")

    async def unlock_elevator(self):
        """Unlocks the elevators."""
        self.building.lock_elevators = False
        print("BMSAgent: Elevators unlocked.")
            
    async def lock_doors(self):
        """Locks the doors."""
        if not self.elevator_locked:
            self.building.lock_doors=True
            print("BMSAgent: doors locked due to emergency.")

    async def unlock_doors(self):
        """Unlocks the doors."""
        self.building.lock_doors = False
        print("BMSAgent: doors unlocked.")


    async def setup(self):
        """Sets up the behaviors for the BMSAgent."""
        print("BMSAgent: Starting...")
        self.add_behaviour(self.ReceiveEmergencyMessages())
