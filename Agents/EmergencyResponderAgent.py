from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from abuilding import Room, Building

class EmergencyResponderAgent(Agent):
    def __init__(self, jid, password, role, building: Building):
        super().__init__(jid, password)
        self.role = role  # "cop" ou "fireman"
        self.building = building  # Referência ao edifício
        self.location = self.building.layout[0][0][0]  # Começa no primeiro andar, primeira sala

    class RespondToBMSAlertBehaviour(CyclicBehaviour):
        async def run(self):
            """Responde a alertas do BMS."""
            print(f"{self.agent.role.capitalize()} responder is ready.")
            alert = await self.receive(timeout=20)
            if alert and "Emergency" in alert.body:
                print(f"{self.agent.role.capitalize()} responder: Emergency alert received.")
                # Lógica de resposta ao alerta será implementada aqui.

    async def assist_occupants(self):
        #Ajuda ocupantes a encontrarem a saída.
        print(f"{self.role.capitalize()} responder is assisting occupants to find exits.")
        for floor in self.building.layout:
            for row in floor:
                for room in row:
                    if room and room.room_type == "H":
                        print(f"{self.role.capitalize()} responder: Checking room ({room.row}, {room.col}).")
                        # Aqui poderia ser adicionada lógica para interação com os ocupantes.

    async def respond_to_emergency(self, emergency_type, target_room: Room):
        #Responde a uma emergência específica.
        print(f"{self.role.capitalize()} responder is responding to {emergency_type} in room ({target_room.row}, {target_room.col}).")
        await self.navigate_to_room(target_room)

    async def navigate_to_room(self, target_room: Room):
        #Navega para uma sala-alvo.
        print(f"{self.role.capitalize()} responder is navigating to room ({target_room.row}, {target_room.col}).")
        while self.location != target_room:
            next_room = self.go_to_next_room(target_room)
            if next_room is None:
                print(f"{self.role.capitalize()} responder: No path to the target room!")
                return
            await asyncio.sleep(1)  # Simula o movimento
            print(f"{self.role.capitalize()} responder moved from ({self.location.row}, {self.location.col}) to ({next_room.row}, {next_room.col}).")
            self.location = next_room
        print(f"{self.role.capitalize()} responder arrived at room ({target_room.row}, {target_room.col}).")

    def go_to_next_room(self, target_room: Room):
        #Calcula o próximo movimento em direção à sala-alvo.
        current_row, current_col = self.location.row, self.location.col
        target_row, target_col = target_room.row, target_room.col
        next_row, next_col = current_row, current_col
        # Define direção
        if current_row < target_row:
            next_row += 1
        elif current_row > target_row:
            next_row -= 1
        if current_col < target_col:
            next_col += 1
        elif current_col > target_col:
            next_col -= 1
        # Retorna a próxima sala
        try:
            next_room = self.building.layout[self.location.floor][next_row][next_col]
            if next_room and next_room.room_type == "H":  # Apenas corredores são transitáveis
                return next_room
        except IndexError:
            pass
        return None

    async def setup(self):
        #Configura comportamentos do agente.
        print(f"{self.role.capitalize()} responder agent started...")
        self.add_behaviour(self.RespondToBMSAlertBehaviour())
