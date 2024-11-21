from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from abuilding import Room, Building


class EmergencyResponderAgent(Agent):
    def __init__(self, jid, password, role, building: Building):
        super().__init__(jid, password)
        self.role = role  # "cop", "fireman", "earthquake_responder", "gas_responder", "it_responder"
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
                    await self.agent.send_resolution_status("Fire", target_room)

                elif txt.body.startswith("Earthquake") and self.agent.role == 'fireman':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    await self.agent.navigate_to_room(target_room)
                    print(f"{self.agent.role.capitalize()} responder is responding to Earthquake")
                    print(f"{self.agent.role.capitalize()} Everyone at the room is safe")
                    await self.agent.send_resolution_status("Earthquake", target_room)

                elif txt.body.startswith("Security Threat") and self.agent.role == 'cop':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    await self.agent.navigate_to_room(target_room)
                    print(f"{self.agent.role} responder is responding to security threat in Room: {target_floor},{target_row},{target_col}.")
                    print(f"{self.agent.role} Security threat in Room: {target_floor},{target_row},{target_col} resolved.")
                    await self.agent.send_resolution_status("Security Threat", target_room)

                # Additional conditions for gas leaks or informatic attacks could be handled similarly
                elif txt.body.startswith("Gas Leak") and self.agent.role == 'gas_responder':
                    print(f"{self.agent.role.capitalize()} responder is addressing gas leak.")
                    await self.agent.send_resolution_status("Gas Leak", None)

                elif txt.body.startswith("Informatic Attack") and self.agent.role == 'it_responder':
                    print(f"{self.agent.role.capitalize()} responder is addressing informatic attack.")
                    await self.agent.send_resolution_status("Informatic Attack", None)

    async def send_resolution_status(self, emergency_type, room=None):
        """Envio de mensagem ao BMS indicando que a emergência foi resolvida."""
        msg = Message(to="bms@localhost")
        if emergency_type in ["Fire", "Earthquake", "Security Threat"]:
            if room:
                msg.body = f"Emergency:{emergency_type} resolved, Location: {room.row},{room.col},{room.floor}"
                print(f"EmergencyResponder: Mensagem enviada ao BMS sobre {emergency_type} resolvido na sala ({room.row},{room.col},{room.floor}).")
        else:
            msg.body = f"Emergency:{emergency_type} resolved"
            print(f"EmergencyResponder: Mensagem enviada ao BMS sobre {emergency_type} resolvido.")
        
        await self.send(msg)

    async def check_elevator_availability(self, target_floor):
        # Solicita ao BMSAgent o estado do elevador.
        message = Message(to="bms@localhost")
        message.body = "Elevator Request"
        await self.send(message)
        print(f"{self.role.capitalize()} responder: Requesting elevator status from BMSAgent.")
        reply = await self.receive(timeout=5)  # Aguarda resposta
        if reply and reply.body == "Elevator Unlocked":
            print(f"{self.role.capitalize()} responder: Elevator available. Using elevator.")
            includes_elevator = True
        else:
            print(f"{self.role.capitalize()} responder: Elevator unavailable. Using stairs.")
            includes_elevator = False
        return self.find_nearest_vertical_connection(includes_elevator)

    async def navigate_to_room(self, target_room):
        while self.location != target_room:
            if self.location.floor != target_room.floor:
                transition_room = await self.check_elevator_availability(target_room.floor)
                if not transition_room:
                    print(f"{self.role.capitalize()} responder: No transition available.")
                    return
                await self.navigate_to_room(transition_room)
                if transition_room.elevators:
                    await self.use_elevator(target_room.floor)
                elif transition_room.staircases:
                    await self.use_stairs(target_room.floor)
            else:
                if not self.go_to_next_room(target_room):
                    print(f"{self.role.capitalize()} responder: Couldn't reach Room {target_room.row},{target_room.col}.")
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
            print(f"{self.role.capitalize()} responder: No transition options available.")
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
