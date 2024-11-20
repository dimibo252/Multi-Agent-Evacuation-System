from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from abuilding import Room, Building
from BMSAgent import elevator_locked


class EmergencyResponderAgent(Agent):
    def __init__(self, jid, password, role, building: Building):
        super().__init__(jid, password)
        self.role = role  # "cop" ou "fireman"
        self.building = building  # Referência ao edifício
        self.location = self.building.layout[0][0][0]  # Começa no primeiro andar, primeira sala

    class EmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            txt = await self.receive(timeout=0.3)
            if txt:
                if txt.body.startswith("Fire") and self.agent.role == 'fireman':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    await self.agent.navigate_to_room(target_room)
                    print(f"{self.agent.role} responder is responding to fire in Room: {target_floor},{target_row},{target_col}.")
                    print(f"{self.agent.role} Fire at Room: {target_floor},{target_row},{target_col} extinguished.")
                    #self.agent.environment.responses+=1
                    #self.agent.environment.num_fires[0]+=1
                    #room.is_on_fire = False
                    #room.noted_fire = False
                
                elif txt.body.startswith("Earthquake") and self.agent.role == 'cop':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    await self.agent.navigate_to_room(target_room)
                    print(f"{self.agent.role.capitalize()} responder is responding to Earthquake")
                    print(f"{self.agent.role.capitalize()} Everyone at the building is safe")
                    #self.agent.environment.responses+=1
                    #self.agent.environment.num_earthquakes[0]+=1
                    #room.is_damaged = False
                    #room.noted_earthquake = False
                
                elif txt.body.startswith("Invasion") and self.agent.role == 'cop':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    await self.agent.navigate_to_room(target_room)
                    print(f"{self.agent.role} responder is responding to invasion in Room: {target_floor},{target_row},{target_col}.")
                    print(f"{self.agent.role} Invasion at Room: {target_floor},{target_row},{target_col} resolved.")
                    #self.agent.environment.num_attacks[0]+=1
                    #self.agent.environment.responses+=1
                    #room.is_taken = False
                    #room.noted_attack = False

    async def navigate_to_room(self, target_room):
        while self.location != target_room:
            if self.location.floor != target_room.floor:
                # Precisa mudar de andar
                if not elevator_locked:
                    transition_room = self.find_nearest_vertical_connection(includes_elevator=True)
                else:
                    transition_room = self.find_nearest_vertical_connection(includes_elevator=False)
                
                if not transition_room:
                    print(f"{self.role.capitalize()} responder: Não foi possível encontrar um meio de transição.")
                    return
                await self.navigate_to_room(transition_room)
                # Usar elevador ou escada para mudar de andar
                if transition_room.elevators and not elevator_locked:
                    await self.use_elevator(target_room.floor)
                elif transition_room.staircases:
                    await self.use_stairs(target_room.floor)
                else:
                    print(f"{self.role.capitalize()} responder: Erro na transição de andar.")
                    return
            else:
                # Navegar no mesmo andar
                if not self.go_to_next_room(target_room):
                    print(f"{self.role.capitalize()} responder: Não foi possível alcançar a sala {target_room.row},{target_room.col}.")
                    return
            await asyncio.sleep(1)

    def go_to_next_room(self, target_room):
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
            if next_room and next_room.room_type == "H":  # Apenas corredores são transitáveis
                self.location = next_room
                print(f"{self.role.capitalize()} responder moved to Room ({next_row}, {next_col}).")
                return True
        except IndexError:
            pass
        return False

    def find_nearest_vertical_connection(self, includes_elevator=True):
        current_floor = self.building.layout[self.location.floor]
        options = [
            room for row in current_floor for room in row
            if room and (room.staircases or (room.elevators if includes_elevator else False))
        ]
        if not options:
            print(f"{self.role.capitalize()} responder: Não há opções de transição disponíveis.")
            return None
        return min(
            options,
            key=lambda room: abs(room.row - self.location.row) + abs(room.col - self.location.col)
        )

    async def use_elevator(self, destination_floor):
        print(f"{self.role.capitalize()} responder is using the elevator to floor {destination_floor}.")
        await asyncio.sleep(4)  # Simula o tempo do elevador
        self.location = self.building.layout[destination_floor][self.location.row][self.location.col]

    async def use_stairs(self, destination_floor):
        print(f"{self.role.capitalize()} responder is using stairs to floor {destination_floor}.")
        await asyncio.sleep(2 * abs(destination_floor - self.location.floor))  # Simula o tempo para usar as escadas
        self.location = self.building.layout[destination_floor][self.location.row][self.location.col]

    async def setup(self):
        print(f"{self.role.capitalize()} responder agent started...")
        self.add_behaviour(self.EmergencyBehaviour())
