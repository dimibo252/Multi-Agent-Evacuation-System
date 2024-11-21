from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from building import Room, Building


class EmergencyResponderAgent(Agent):
    def __init__(self, jid, password, role, building: Building):
        super().__init__(jid, password)
        self.role = role  # "cop", "fireman", "earthquake_responder", "gas_responder", "it_responder"
        self.building = building  # Referência ao edifício
        self.location = self.building.layout[0][0][0] # Começa no primeiro andar, primeira sala
        self.pace=0.5
        self.type="Responder"

    class EmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            txt = await self.receive(timeout=0.3)
            if txt:
                if txt.body.startswith("Fire") and self.agent.role == 'fireman':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    print(f"{self.agent.role} responder is responding to fire in Room: {target_floor},{target_row},{target_col}.")
                    await self.navigate_to_room(target_room)
                    print(f"{self.agent.role} Fire at Room: {target_floor},{target_row},{target_col} extinguished.")
                    await self.send_resolution_status("Fire", target_room)

                elif txt.body.startswith("Earthquake") and self.agent.role == 'fireman':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    print(f"{self.agent.role.capitalize()} responder is responding to Earthquake")
                    await self.navigate_to_room(target_room)
                    print(f"{self.agent.role.capitalize()} Everyone at the room is safe")
                    await self.send_resolution_status("Earthquake", target_room)

                elif txt.body.startswith("Security Threat") and self.agent.role == 'cop':
                    _, room_coords = txt.body.split("Room:")
                    target_floor, target_row, target_col = map(int, room_coords.split(","))
                    target_room = self.agent.building.layout[target_floor][target_row][target_col]
                    print(f"{self.agent.role} responder is responding to security threat in Room: {target_floor},{target_row},{target_col}.")
                    await self.navigate_to_room(target_room)
                    print(f"{self.agent.role} Security threat in Room: {target_floor},{target_row},{target_col} resolved.")
                    await self.send_resolution_status("Security Threat", target_room)

                # Additional conditions for gas leaks or informatic attacks could be handled similarly
                elif txt.body.startswith("Gas Leak") and self.agent.role == 'gas_responder':
                    print(f"{self.agent.role.capitalize()} responder is addressing gas leak.")
                    await self.send_resolution_status("Gas Leak", None)

                elif txt.body.startswith("Informatic Attack") and self.agent.role == 'it_responder':
                    print(f"{self.agent.role.capitalize()} responder is addressing informatic attack.")
                    await self.send_resolution_status("Informatic Attack", None)

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
            
        async def navigate_to_room(self, target_room):
            """Navega até uma sala específica no mesmo andar."""
            while self.agent.location != target_room:
                self.go_to_next_room(target_room)
                await asyncio.sleep(self.agent.pace)
            self.agent.location.fire = False #apaga o fogo ou faz uma passagem noq foi destruido
            self.agent.location.unavailable = False  

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
            
            for connection in connections:
                connection.fire=False #fix the fires or damaged paths that are on their path
                connection.unavailable=False
            
            nearest_connection = min(
                connections,
                key=lambda pos: abs(pos.row - target_row) + abs(pos.col - target_col) + abs(pos.floor - target_floor)
            )
            
            self.agent.location=nearest_connection
            return True
            

    async def setup(self):
        print(f"{self.role.capitalize()} responder agent started...")
        self.add_behaviour(self.EmergencyBehaviour())
