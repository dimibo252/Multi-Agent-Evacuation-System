from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import random


class EmergencyAgent(Agent):
    def __init__(self, jid, password, building):
        super().__init__(jid, password)
        self.building = building  # Reference to the building
        self.emergency_type = None
        self.hacked_systems = []  # Track affected systems for informatic attacks

    class EmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            """Manage emergencies and dynamic conditions."""
            await asyncio.sleep(5)  # Delay to allow setup
            if not self.agent.emergency_type:
                # Start an emergency
                self.agent.emergency_type = self.agent.start_emergency()
                print(f"Emergency initiated: {self.agent.emergency_type}")

            # Update dynamic emergency conditions
            rn=random.random()
            if rn < 0.01:
                self.agent.start_fire()
            elif rn <0.02:
                self.agent.update_informatic_attack()

    def start_emergency(self):
        """Start an emergency by selecting a random type."""
        emergencies = {
            "Fire": 0.35,
            "Earthquake": 0.25,
            "Gas Leak": 0.2,
            "Security Threat": 0.1,
            "Informatic Attack": 0.1,
        }
        self.emergency_type = random.choices(list(emergencies.keys()), weights=emergencies.values(), k=1)[0]
        if self.emergency_type == "Fire":
            self.start_fire()
        elif self.emergency_type == "Earthquake":
            self.start_earthquake()
        elif self.emergency_type == "Gas Leak":
            pass
            #When its a gas leak, just evacuate
        elif self.emergency_type == "Security Threat":
            self.start_security_threat()
        elif self.emergency_type == "Informatic Attack":
            self.start_informatic_attack()
        return self.emergency_type

    def start_informatic_attack(self):
        """Start an informatic attack targeting random building systems."""
        systems = ["doors", "communication", "elevators"]
        self.hacked_systems = random.sample(systems, k=random.randint(1, len(systems)))
        for system in self.hacked_systems:
            if system == "doors":
                self.building.lock_doors = True
            elif system == "elevators":
                self.building.lock_elevators = True
            elif system == "communication":
                self.building.lock_communications = True
        print(f"Informatic attack targets: {self.hacked_systems}")

    def update_informatic_attack(self):
        """Simulate ongoing informatic attack effects."""
        rn=random.random()
        if rn < 0.33:
            self.building.lock_doors=True
        elif rn < 0.66:
            self.building.lock_communications=True
        else:
            self.building.lock_elevators = True

    def start_fire(self):
        """Start a fire using `building.py` methods."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            fire_room = random.choice(unoccupied_rooms)
            fire_room.fires()  # Call the method from building.py
            print(f"Fire started in room ({fire_room.row}, {fire_room.col}, Floor {fire_room.floor})")

    def start_earthquake(self):
        """Simulate an earthquake using `building.py` methods."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            room = random.choice(unoccupied_rooms)
            room.earthquake()  # Call the method from building.py
        print("Earthquake damage applied to all rooms.")

    def start_security_threat(self):
        """Simulate a security threat in specific areas."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            room = random.choice(unoccupied_rooms)
            room.security_threath()
    # Indicate the room is under a security threat
        print("Security threat initiated.")

    def get_unoccupied_rooms(self, room_type=None):
        """
        Get a list of unoccupied rooms of a specific type (e.g., "H").
        Excludes rooms marked as occupied.
        """
        return [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and not room.is_occupied and (room_type is None or room.room_type == room_type)
        ]

    async def setup(self):
        """Setup the EmergencyBehaviour for the agent."""
        print("EmergencyAgent started.")
        self.add_behaviour(self.EmergencyBehaviour())
