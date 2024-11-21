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
        self.hacked_systems = []  # Track systems affected by informatic attacks

    class EmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            """Manages emergencies and dynamic conditions."""
            if not self.agent.emergency_type:
                # Start an emergency if none is active
                self.agent.emergency_type = await self.agent.start_emergency()
                print(f"Emergency initiated: {self.agent.emergency_type}")

            # Update dynamic conditions every 5 seconds
            await asyncio.sleep(5)

            # Simulate dynamic emergency updates
            rn = random.random()
            if rn < 0.01:
                await self.agent.start_fire()
            elif rn < 0.02:
                await self.agent.update_informatic_attack()
            elif rn < 0.03:
                await self.agent.start_earthquake()

    async def start_emergency(self):
        """Starts an emergency by selecting a random type."""
        emergencies = {
            "Fire": 0.35,
            "Earthquake": 0.25,
            "Gas Leak": 0.2,
            "Security Threat": 0.1,
            "Informatic Attack": 0.1,
        }

        self.emergency_type = random.choices(list(emergencies.keys()), weights=emergencies.values(), k=1)[0]

        await self.send_emergency_to_bms(self.emergency_type)

        if self.emergency_type == "Fire":
            await self.start_fire()
        elif self.emergency_type == "Earthquake":
            await self.start_earthquake()
        elif self.emergency_type == "Gas Leak":
            pass  # Evacuation only
        elif self.emergency_type == "Security Threat":
            await self.start_security_threat()
        elif self.emergency_type == "Informatic Attack":
            await self.start_informatic_attack()

        return self.emergency_type

    async def send_emergency_to_bms(self, emergency_type, room=None):
        """
        Sends an emergency message to the BMSAgent with the emergency type and location.
        """
        msg = Message(to="bms@localhost")  # Replace with the actual BMS JID
        msg.set_metadata("performative", "inform")  # Inform the BMS
        msg.set_metadata("protocol", "emergency_alert")
        msg.body = f"Emergency:{emergency_type}"

        if room:
            msg.body += f",Location:{room.row},{room.col},{room.floor}"
            print(f"EmergencyAgent: Sent {emergency_type} alert for room ({room.row}, {room.col}, Floor {room.floor})")
        else:
            print(f"EmergencyAgent: Sent {emergency_type} alert.")

        await self.send(msg)

    async def start_informatic_attack(self):
        """Starts an informatic attack on random building systems."""
        systems = ["doors", "communication", "elevators"]
        self.hacked_systems = random.sample(systems, k=random.randint(1, len(systems)))
        await self.send_emergency_to_bms("Informatic Attack")
        for system in self.hacked_systems:
            if system == "doors":
                self.building.lock_doors = True
            elif system == "elevators":
                self.building.lock_elevators = True
            elif system == "communication":
                self.building.lock_communications = True
        print(f"Informatic attack targets: {self.hacked_systems}")

    async def update_informatic_attack(self):
        """Simulates ongoing effects of informatic attacks."""
        rn = random.random()
        if rn < 0.33:
            self.building.lock_doors = True
        elif rn < 0.66:
            self.building.lock_communications = True
        else:
            self.building.lock_elevators = True

    async def start_fire(self):
        """Starts a fire in an unoccupied room."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            fire_room = random.choice(unoccupied_rooms)
            fire_room.fires()  # Call the method from `Room`
            await self.send_emergency_to_bms("Fire", fire_room)
            print(f"Fire started in room ({fire_room.row}, {fire_room.col}, Floor {fire_room.floor})")

    async def start_earthquake(self):
        """Simulates an earthquake across all rooms."""
        for floor in self.building.layout:
            for row in floor:
                for room in row:
                    if room:
                        room.earthquake()
        await self.send_emergency_to_bms("Earthquake")
        print("Earthquake damage applied to all rooms.")

    async def start_security_threat(self):
        """Simulates a security threat in a random unoccupied room."""
        unoccupied_rooms = self.get_unoccupied_rooms()
        if unoccupied_rooms:
            security_room = random.choice(unoccupied_rooms)
            security_room.security_threath()
            await self.send_emergency_to_bms("Security Threat", security_room)
            print(f"Security threat initiated in room ({security_room.row}, {security_room.col}, Floor {security_room.floor})")

    def get_unoccupied_rooms(self, room_type=None):
        """
        Gets a list of unoccupied rooms of a specific type.
        """
        return [
            room
            for floor in self.building.layout
            for row in floor
            for room in row
            if room and not room.is_occupied and (room_type is None or room.room_type == room_type)
        ]

    async def setup(self):
        """Sets up the EmergencyBehaviour for the agent."""
        print("EmergencyAgent started.")
        self.add_behaviour(self.EmergencyBehaviour())
