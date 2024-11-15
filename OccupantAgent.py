from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class OccupantAgent(Agent):
    # Listen for emergency alerts from BMS and request exit information if alerted
    class ListenForEmergencyBehaviour(CyclicBehaviour):
        async def run(self):
            alert = await self.receive(timeout=10)
            if alert and "Emergency" in alert.body:
                print("Occupant: Emergency alert received. Requesting exit information...")
                exit_request = Message(to="bms@localhost")
                exit_request.body = "RequestExitInfo"
                await self.send(exit_request)

    # Handle received exit information and reroute if needed
    class RespondToExitInfoBehaviour(CyclicBehaviour):
        async def run(self):
            info = await self.receive(timeout=10)
            if info:
                if "ExitBlocked" in info.body:
                    print("Occupant: Exit is blocked! Rerouting to another exit.")
                else:
                    print(f"Occupant: Exit info received: {info.body}")

    async def setup(self):
        print("Occupant agent started...")
        self.add_behaviour(self.ListenForEmergencyBehaviour())
        self.add_behaviour(self.RespondToExitInfoBehaviour())
