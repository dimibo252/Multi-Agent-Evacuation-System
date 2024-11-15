from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class EmergencyResponderAgent(Agent):
    # Respond to notification from BMS and proceed to assist occupants
    class RespondToBMSAlertBehaviour(CyclicBehaviour):
        async def run(self):
            notification = await self.receive(timeout=10)
            if notification and "Emergency" in notification.body:
                print("Responder: Emergency alert received from BMS. Moving to assist in evacuation.")
                # Here, add logic for responder positioning, occupant support, etc.

    async def setup(self):
        print("Emergency Responder agent started...")
        self.add_behaviour(self.RespondToBMSAlertBehaviour())
