from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import asyncio
import random
import time
from abuilding import Room, Building
from BMSAgent import elevator_locked  # Importa a variável global de BMSAgent.py

class OccupantAgent(Agent):
    def __init__(self, jid, password, agent_name, condition, building: Building):
        super().__init__(jid, password)
        self.agent_name = agent_name
        self.condition = condition  # "disabled" ou "functional"
        self.building = building  # Referência ao edifício
        self.evacuated = False
        self.pace = 10 if condition == "disabled" else 1
        self.finish_time = None
        self.location = self.random_initial_location()  # Define a localização inicial

    def random_initial_location(self):
        # Gera uma localização inicial aleatória em um corredor (`H`).
        available_rooms = [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and room.room_type == "H"
        ]
        if not available_rooms:
            raise ValueError("Não há lugares disponíveis no edifício para posicionar os agentes.")
        return random.choice(available_rooms)

    class ListenForEmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            alert = await self.receive(timeout=20)
            if alert and "Emergency" in alert.body:
                print(f"{self.agent.agent_name}: Emergency alert received.")
                await self.agent.go_to_exit()

    async def go_to_exit(self):
        # Navega até a saída mais próxima.
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
        # Verifica se está no mesmo piso
        if target_floor != self.location.floor:
            # Verifica o estado do elevador através da variável importada
            if not elevator_locked:
                # Elevador funcional: Procura a transition room mais próxima (elevador ou escada)
                transition_room = self.find_nearest_vertical_connection(includes_elevator=True)
            else:
                # Elevador bloqueado: Procura apenas escadas
                transition_room = self.find_nearest_vertical_connection(includes_elevator=False)
            if transition_room:
                await self.navigate_to_room(transition_room)
                # Decide o meio de transição com base no tipo da transition_room
                if transition_room.elevators:
                    await self.use_elevator(target_floor)
                elif transition_room.staircases:
                    await self.use_stairs(target_floor)
                else:
                    print(f"{self.agent_name}: Erro - Transition room inválida.")
            else:
                print(f"{self.agent_name}: Não foi possível encontrar uma maneira de mudar de piso.")
        # Navegar para a saída no piso correto
        print(f"{self.agent_name} está indo para a saída mais próxima em ({target_row}, {target_col}, andar {target_floor}).")
        await self.navigate_to_room(target_room)
        print(f"{self.agent_name} alcançou a saída em ({target_room.row}, {target_room.col}, andar {target_floor}).")
        self.evacuated = True
        self.finish_time = time.time()

    def find_nearest_vertical_connection(self, includes_elevator=True):
        # Encontra a transition room mais próxima (escada ou elevador, dependendo da configuração)."""
        current_floor = self.building.layout[self.location.floor]
        options = [
            room
            for row in current_floor
            for room in row
            if room and (room.staircases or (room.elevators if includes_elevator else False))
        ]
        if not options:
            print(f"{self.agent_name}: Não há opções de transição disponíveis no andar atual.")
            return None
        nearest = min(
            options,
            key=lambda room: abs(room.row - self.location.row) + abs(room.col - self.location.col)
        )
        print(f"{self.agent_name} encontrou a transition room mais próxima em ({nearest.row}, {nearest.col}).")
        return nearest

    async def navigate_to_room(self, target_room):
        # Navega para uma sala específica no mesmo piso.
        while self.location != target_room:
            if not self.go_to_next_room(target_room):
                print(f"{self.agent_name} está preso e não consegue alcançar o destino ({target_room.row}, {target_room.col}).")
                return
            await asyncio.sleep(self.pace)

    def go_to_next_room(self, target_room):
        # Move-se para a próxima sala mais próxima do alvo. 
        current_row, current_col = self.location.row, self.location.col
        target_row, target_col = target_room.row, target_room.col
        next_row, next_col = current_row, current_col
        if current_row < target_row:
            next_row += 1
        elif current_row > target_row:
            next_row -= 1
        if current_col < target_col:
            next_col += 1
        elif current_col > target_col:
            next_col -= 1
        try:
            next_room = self.building.layout[self.location.floor][next_row][next_col]
            if next_room and next_room.room_type == "H":
                self.location = next_room
                print(f"{self.agent_name} moveu-se para a sala ({next_room.row}, {next_room.col}).")
                return True
        except IndexError:
            pass
        return False

    async def use_elevator(self, destination_floor):
        #Usa o elevador para alcançar o andar de destino.
        print(f"{self.agent_name} está esperando pelo elevador no andar {self.location.floor}.")
        await asyncio.sleep(4)  # Simula o tempo do elevador
        self.location = self.building.layout[destination_floor][self.location.row][self.location.col]
        print(f"{self.agent_name} chegou ao andar {destination_floor} pelo elevador.")

    async def use_stairs(self, destination_floor):
        #Usa as escadas para alcançar o andar de destino.
        print(f"{self.agent_name} está subindo as escadas para o andar {destination_floor}.")
        await asyncio.sleep(2 * abs(destination_floor - self.location.floor))  # Simula o tempo para usar as escadas
        self.location = self.building.layout[destination_floor][self.location.row][self.location.col]
        print(f"{self.agent_name} chegou ao andar {destination_floor} pelas escadas.")

    async def setup(self):
        print(f"{self.agent_name} está iniciando na sala ({self.location.row}, {self.location.col}, andar {self.location.floor})...")
        self.add_behaviour(self.ListenForEmergencyBehaviour())
