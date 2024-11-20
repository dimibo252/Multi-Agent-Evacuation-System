from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from abuilding import Building
import random


class DynamicConditionsAgent(Agent):
    def __init__(self, jid, password, building: Building):
        super().__init__(jid, password)
        self.building = building  # Referência ao edifício

    class MonitorBuildingBehaviour(CyclicBehaviour):
        async def run(self):
            """Monitora o edifício para detectar incidentes e notifica o BMS."""
            await asyncio.sleep(5)  # Intervalo para monitorar
            print("DynamicConditions: Monitoring building for incidents.")

            # Simula a detecção de incêndios em salas
            for floor in self.agent.building.layout:
                for row in floor:
                    for room in row:
                        if room and room.room_type == "H":
                            # Probabilidade de 2% de um incêndio ocorrer
                            if random.random() < 0.02:
                                print(f"DynamicConditions: Fire detected in room ({room.row}, {room.col}, {room.floor}).")

                                # Notificar o BMS sobre o incêndio
                                msg = Message(to="bms@localhost")
                                msg.body = f"FireDetected:({room.row}, {room.col}, {room.floor})"
                                await self.send(msg)
                                print(f"DynamicConditions: Sent fire alert to BMS for room ({room.row}, {room.col}, {room.floor}).")

    async def setup(self):
        """Configura o comportamento do agente DynamicConditions."""
        print("DynamicConditions Agent started...")
        self.add_behaviour(self.MonitorBuildingBehaviour())
