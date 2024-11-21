from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import random
import time
from building import Room, Building


class OccupantAgent(Agent):
    def __init__(self, jid, password, agent_name, condition, building: Building):
        super().__init__(jid, password)
        self.agent_name = agent_name
        self.condition = condition  # "disabled" ou "functional"
        self.building = building  # Referência ao edifício
        self.evacuated = False
        self.pace = 2 if condition == "disabled" else 1
        self.finish_time = None
        self.location = self.random_initial_location() # Define a localização inicial
        self.location.is_occupied = True
        self.type="Occupant"
        
    def random_initial_location(self):
        # Gera uma localização inicial aleatória em um corredor (`H`).
        available_rooms = [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room
        ]
        if not available_rooms:
            raise ValueError("Não há lugares disponíveis no edifício para posicionar os agentes.")
        return random.choice(available_rooms)

    class MessageHandlingBehaviour(CyclicBehaviour):
        async def run(self):
            """Recebe e processa mensagens."""
            message = await self.receive(timeout=5)
            if message:
                if "Emergency" in message.body:
                    print(f"{self.agent.agent_name}: Emergency alert received.")
                    await self.handle_emergency_message(message.body)
                elif "Elevator Unlocked" in message.body:
                    print(f"{self.agent.agent_name}: Received elevator availability confirmation.")
                elif "Elevator Locked" in message.body:
                    print(f"{self.agent.agent_name}: Received elevator unavailability confirmation.")
    
        async def handle_emergency_message(self, message_body):
            """Processa uma mensagem de emergência e inicia o processo de evacuação."""
            if "Room:" in message_body:
                _, room_coords = message_body.split("Room:")
                target_floor, target_row, target_col = map(int, room_coords.split(","))
                print(f"{self.agent.agent_name}: Emergency reported near Room ({target_row}, {target_col}, Floor {target_floor}).")
                await self.go_to_exit()
            else:
                print(f"{self.agent_name}: Mensagem de emergência mal formatada ou ausente.")

        async def go_to_exit(self):
            """Navega até a saída mais próxima."""
            exits = [
                (room.row, room.col, room.floor)
                for floor in self.agent.building.layout
                for row in floor
                for room in row
                if room and room.room_type == "E" or "N"
            ]
            if not exits:
                print(f"{self.agent.agent_name}: Não há saídas disponíveis no edifício.")
                return
            nearest_exit = min(
                exits,
                key=lambda pos: abs(pos[0] - self.agent.location.row) + abs(pos[1] - self.agent.location.col) + abs(pos[2] - self.agent.location.floor)
            )
            target_floor, target_row, target_col = nearest_exit[2], nearest_exit[0], nearest_exit[1]
            target_room = self.agent.building.layout[target_floor][target_row][target_col]
            print(f"{self.agent_name} está indo para a saída mais próxima em ({target_row}, {target_col}, andar {target_floor}).")
            if await self.navigate_to_room(target_room):
                print(f"{self.agent_name} alcançou a saída em ({target_room.row}, {target_room.col}, andar {target_floor}).")
                self.agent.evacuated = True
                self.agent.finish_time = time.time()
            else:
                asyncio.wait(100) #wait till emergency responders arrive
                self.go_to_exit()

        async def navigate_to_room(self, target_room):
            """Navega até uma sala específica no mesmo andar."""
            while self.agent.location != target_room:
                if not self.go_to_next_room(target_room):
                    print(f"{self.agent.agent_name} está preso e não consegue alcançar o destino ({target_room.row}, {target_room.col}). Vai ter de esperar que os emergency responders cheguem")
                    return False
                await asyncio.sleep(self.agent.pace)
            return True

        def go_to_next_room(self, target_room):
            target_row, target_col, target_floor = target_room.row, target_room.col, target_room.floor
            room=self.agent.location
            connections = [
                (connection.row, connection.col, connection.floor)
                for connection in room.connections
                if not connection.fire and not connection.unvailable
            ]
            connections.append([
                (connection.row, connection.col, connection.floor)
                for connection in room.elevators
                if not connection.fire and not connection.unvailable and not self.agent.building.lock_elevators
            ])
            connections.append([
                (connection.row, connection.col, connection.floor)
                for connection in room.staircases
                if not connection.fire and not connection.unvailable
            ])
            connections.append([
                (connection.row, connection.col, connection.floor)
                for connection in room.emergency_staircases
                if not connection.fire and not connection.unvailable and not self.agent.building.lock_doors
            ])
            
            if not connections:
                print(f"{self.agent.agent_name}: Não há saídas disponíveis no edifício.")
                return False
            
            nearest_connection = min(
                connections,
                key=lambda pos: abs(pos.row - target_row) + abs(pos.col - target_col) + abs(pos.floor - target_floor)
            )
            
            self.agent.location=nearest_connection
            return True
            

    async def setup(self):
        print(f"{self.agent_name} está iniciando na sala ({self.location.row}, {self.location.col}, andar {self.location.floor})...")
        self.add_behaviour(self.MessageHandlingBehaviour())
