from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import random
import time
from abuilding import Room, Building

class OccupantAgent(Agent):
    def __init__(self, jid, password, agent_name, condition, building: Building):
        super().__init__(jid, password)
        self.agent_name = agent_name
        self.condition = condition  # "disabled" ou "functional"
        self.building = building  # Referência ao edifício
        self.evacuated = False
        self.pace = 10 if condition == "disabled" else 1
        self.is_evacuated = False
        self.finish_time = None
        self.location = self.random_initial_location()  # Define a localização inicial

    def random_initial_location(self):
        """Gera uma localização inicial aleatória em um corredor (`H`)."""
        available_rooms = [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and room.room_type == "H"
        ]
        # Escolhe uma sala aleatória para o agente
        if not available_rooms:
            raise ValueError("Não há corredores disponíveis no edifício para posicionar os agentes.")
        return random.choice(available_rooms)

    class ListenForEmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            alert = await self.receive(timeout=20)
            if alert and "Emergency" in alert.body:
                print(f"{self.agent.agent_name}: Emergency alert received.")
                await self.agent.go_to_exit()

    async def go_to_exit(self):
        """Navega até a saída mais próxima."""
        exits = [
            (room.row, room.col, floor_index)
            for floor_index, floor in enumerate(self.building.layout)
            for row in floor
            for room in row
            if room and room.room_type == "E"
        ]
        if not exits:
            print(f"{self.agent_name}: Não há saídas disponíveis no edifício.")
            return
        
        # Encontra a saída mais próxima considerando todos os pisos
        nearest_exit = min(
            exits,
            key=lambda pos: abs(pos[0] - self.location.row) + abs(pos[1] - self.location.col) + abs(pos[2] - self.location.floor)
        )
        target_floor, target_row, target_col = nearest_exit[2], nearest_exit[0], nearest_exit[1]
        target_room = self.building.layout[target_floor][target_row][target_col]

        # Altera o andar, se necessário
        if target_floor != self.location.floor:
            if self.condition == "disabled" and not self.building.elevator_locked:
                await self.use_elevator(target_floor)
            else:
                await self.use_stairs(target_floor)

        # Navega até a saída no mesmo piso
        print(f"{self.agent_name} está indo para a saída mais próxima em ({target_row}, {target_col}, andar {target_floor}).")
        while self.location != target_room:
            if not self.go_to_next_room(target_room):
                print(f"{self.agent_name} está preso e não consegue alcançar a saída.")
                return
            await asyncio.sleep(self.pace)

        print(f"{self.agent_name} alcançou a saída em ({target_room.row}, {target_room.col}, andar {target_floor}).")
        self.evacuated = True
        self.finish_time = time.time()

    def go_to_next_room(self, target_room):
        """Move-se para a próxima sala mais próxima do alvo."""
        current_row, current_col = self.location.row, self.location.col
        target_row, target_col = target_room.row, target_room.col
        next_row, next_col = current_row, current_col
        # Determina a direção
        if current_row < target_row:
            next_row += 1
        elif current_row > target_row:
            next_row -= 1
        if current_col < target_col:
            next_col += 1
        elif current_col > target_col:
            next_col -= 1
        # Atualiza a localização
        try:
            next_room = self.building.layout[self.location.floor][next_row][next_col]
            if next_room and next_room.room_type in {"H", "E"}:  # Move apenas para corredores ou saídas
                self.location = next_room
                print(f"{self.agent_name} moveu-se para a sala ({next_room.row}, {next_room.col}).")
                return True
        except IndexError:
            pass
        return False

    async def use_elevator(self, destination_floor):
        """Usa o elevador para alcançar o andar de destino."""
        print(f"{self.agent_name} está esperando pelo elevador no andar {self.location.floor}.")
        await asyncio.sleep(4)  # Simula o tempo do elevador
        self.location = self.building.layout[destination_floor][self.location.row][self.location.col]
        print(f"{self.agent_name} chegou ao andar {destination_floor} pelo elevador.")

    async def use_stairs(self, destination_floor):
        """Usa as escadas para alcançar o andar de destino."""
        print(f"{self.agent_name} está subindo as escadas para o andar {destination_floor}.")
        await asyncio.sleep(2 * abs(destination_floor - self.location.floor))  # Simula o tempo para usar as escadas
        self.location = self.building.layout[destination_floor][self.location.row][self.location.col]
        print(f"{self.agent_name} chegou ao andar {destination_floor} pelas escadas.")

    async def setup(self):
        print(f"{self.agent_name} está iniciando na sala ({self.location.row}, {self.location.col}, andar {self.location.floor})...")
        self.add_behaviour(self.ListenForEmergencyBehaviour())
