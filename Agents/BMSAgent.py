from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from abuilding import Building, Room
import random

class BMSAgent(Agent):
    def __init__(self, jid, password, building: Building, role):
        super().__init__(jid, password)
        self.building = building
        self.role = role
        self.elevator_locked = False

    class ElevatorManager(CyclicBehaviour):
        async def run(self):
            message = await self.receive(timeout=0.5)
            if message and message.body.startswith("Elevator Request"):
                if not self.agent.elevator_locked:
                    await self.unlock_elevator()
                    reply = Message(to=str(message.sender))
                    reply.body = "Elevator Unlocked"
                    await self.send(reply)
                    print("Elevator unlocked for use.")
                else:
                    print("Elevator is locked.")

        async def unlock_elevator(self):
            self.agent.elevator_locked = False

        async def lock_elevator(self):
            self.agent.elevator_locked = True

    class ManageBuilding(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(0.5)  # Frequência de verificação
            for floor in self.agent.building.layout:
                for row in floor:
                    for room in row:
                        if room:
                            # Detectar incêndio
                            if room.fire:
                                print(f"Fire detected in room ({room.row}, {room.col}, {room.floor})!")
                                await self.agent.notify_emergency(room, "Fire")
                            
                            # Detectar terremoto
                            if room.unavailable:  # Para situações como terremotos
                                print(f"Earthquake damage in room ({room.row}, {room.col}, {room.flor})!")
                                await self.agent.notify_emergency(room, "Earthquake")

                            # Detectar invasão
                            if room.room_type == "H" and random.random() < 0.01:  # Exemplo de invasão aleatória
                                print(f"Invasion detected in room ({room.row}, {room.col}, {room.floor})!")
                                await self.agent.notify_emergency(room, "Invasion")

        async def notify_emergency(self, room, disaster_type):
            """
            Notifica ocupantes e agentes de emergência sobre o desastre detectado.
            """
            message_body = f"{disaster_type} Room: {room.floor},{room.row},{room.col}"
            print(f"Sending notification: {message_body}")

            # Notificar ocupantes
            for occupant in self.building.agents:
                if occupant:
                    occupant_message = Message(to=occupant.jid)
                    occupant_message.body = message_body
                    await self.send(occupant_message)

            # Notificar agentes de emergência
            for emergency_agent in self.building.emergency_agents:
                if emergency_agent:
                    emergency_message = Message(to=emergency_agent.jid)
                    emergency_message.body = message_body
                    await self.send(emergency_message)


    async def setup(self):
        """
        Configura os comportamentos do BMSAgent.
        """
        print("BMS Agent is starting...")
        self.add_behaviour(self.ElevatorManager())
        self.add_behaviour(self.ManageBuilding())
