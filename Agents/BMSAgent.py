from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
from abuilding import Building, Room
from collections import deque


class BMSAgent(Agent):
    def __init__(self, jid, password, building: Building):
        super().__init__(jid, password)
        self.building = building  # Referência ao edifício
        self.elevator_locked = False
        # Inicializa o status das saídas
        self.exit_status = {
            room: "open"
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and room.room_type == "H"
        }

    class ProcessIncidentBehaviour(CyclicBehaviour):
        async def run(self):
            """Processa notificações de incidentes recebidas."""
            msg = await self.receive(timeout=10)
            if msg:
                try:
                    # Verifica se a mensagem é de incêndio
                    if "FireDetected" in msg.body:
                        # Extrai as coordenadas da sala
                        room_coords = eval(msg.body.split(":")[1])  # Exemplo: "FireDetected:(3, 2, 0)"
                        room = self.agent.building.layout[room_coords[2]][room_coords[0]][room_coords[1]]
                        print(f"BMS: Received fire alert for room ({room.row}, {room.col}, {room.floor}).")
                        # Bloqueia elevadores
                        self.agent.elevator_locked = True
                        print("BMS: Elevators locked due to fire.")
                        # Notifica os respondentes
                        responders = ["fireman@localhost"]
                        for responder in responders:
                            alert_msg = Message(to=responder)
                            alert_msg.body = f"FireAlert: Fire in room ({room.row}, {room.col}, {room.floor})."
                            await self.send(alert_msg)
                            print(f"BMS: Notified {responder} about fire in room ({room.row}, {room.col}, {room.floor}).")
                        # Atualiza o status da sala
                        self.agent.exit_status[room] = "blocked"
                        print(f"BMS: Room ({room.row}, {room.col}, {room.floor}) marked as blocked.")
                except Exception as e:
                    print(f"BMS: Error processing incident message - {e}")

    def find_alternative_route(self, start_room: Room):
        """Calcula a rota alternativa mais próxima para uma saída aberta."""
        visited = set()
        queue = deque([(start_room, [])])  # Fila de BFS: (sala atual, caminho até aqui)
        while queue:
            current_room, path = queue.popleft()
            if current_room in visited:
                continue
            visited.add(current_room)
            # Verifica se a sala atual é uma saída aberta
            if self.exit_status.get(current_room, "blocked") == "open":
                return path + [current_room]
            # Adiciona vizinhos à fila
            for neighbor in current_room.connections:
                if neighbor not in visited:
                    queue.append((neighbor, path + [current_room]))
        return None  # Caso nenhuma saída seja encontrada

    async def setup(self):
        """Configura comportamentos iniciais do agente BMS."""
        print("BMS Agent started...")
        process_behaviour = self.ProcessIncidentBehaviour()
        self.add_behaviour(process_behaviour)
