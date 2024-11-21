import heapq
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import random
import time
from building import Room, Building

class TreeNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node.state)
            node = node.parent
        return list(reversed(path_back))

def greedy_search(building, start, heuristic):
    setattr(TreeNode, "__lt__", lambda self, other: heuristic(self) < heuristic(other))
    states = [TreeNode(start)]
    visited = set()
    while states:
        current = heapq.heappop(states)
        if current.state in building.exits:
            return current.path()
        visited.add(current.state)
        for neighbor in building.connections.get(current.state, []):
            if neighbor not in visited and neighbor not in building.unavailable:
                child_node = TreeNode(state=neighbor, parent=current)
                current.add_child(child_node)
                heapq.heappush(states, child_node)
    return None

def heuristic(node, building):
    current_position = node.state
    return min(building.distances[current_position][exit] for exit in building.exits)

class OccupantAgent(Agent):
    def __init__(self, jid, password, agent_name, condition, building: Building):
        super().__init__(jid, password)
        self.agent_name = agent_name
        self.condition = condition
        self.building = building
        self.evacuated = False
        self.pace = 10 if condition == "disabled" else 1
        self.finish_time = None
        self.location = self.random_initial_location()
        self.bms_jid = "bms@localhost"

    def random_initial_location(self):
        available_rooms = [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and room.room_type == "H"
        ]
        if not available_rooms:
            raise ValueError("No available locations in the building for agents.")
        return random.choice(available_rooms)

    class ListenForEmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            alert = await self.receive(timeout=20)
            if alert and "Emergency" in alert.body:
                print(f"{self.agent.agent_name}: Emergency alert received.")
                await self.agent.go_to_exit()

    async def go_to_exit(self):
        start = (self.location.row, self.location.col, self.location.floor)
        path = greedy_search(self.building, start, lambda node: heuristic(node, self.building))
        if not path:
            print(f"{self.agent_name}: Could not find a path to the exit.")
            return
        for step in path:
            await asyncio.sleep(self.pace)
            self.location = self.building.get_room(step)
            print(f"{self.agent_name} moved to room ({self.location.row}, {self.location.col}, floor {self.location.floor}).")
        print(f"{self.agent_name} has evacuated the building.")
        self.evacuated = True
        self.finish_time = time.time()

    async def setup(self):
        print(f"{self.agent_name} is starting in room ({self.location.row}, {self.location.col}, floor {self.location.floor})...")
        self.add_behaviour(self.ListenForEmergencyBehaviour())