from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
import asyncio


class BMSAgent(Agent):
    # Behavior to trigger an initial emergency alert to Occupant and Responder agents
    class EmergencyAlertBehaviour(OneShotBehaviour):
        async def run(self):
            await asyncio.sleep(10)  # Initial delay for demonstration
            alert_msg = Message(to="occupant@localhost")
            alert_msg.body = "Emergency: Evacuate the building"
            await self.send(alert_msg)
            print("BMS: Sent initial emergency alert to Occupant.")

            responder_msg = Message(to="responder@localhost")
            responder_msg.body = "Emergency: Respond to building for evacuation"
            await self.send(responder_msg)
            print("BMS: Notified Emergency Responder.")

    # Provide exit information to Occupant when requested
    class ProvideExitInfoBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.body == "RequestExitInfo":
                print(f"BMS: Received exit info request from {msg.sender}.")
                response = Message(to=str(msg.sender))
                response.body = "Exit A is available"  # Initial route
                await self.send(response)
                print("BMS: Sent exit info to Occupant.")

    # Dynamic condition behaviour to simulate blocked exits and update Occupants
    class DynamicConditionBehaviour(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(20)  # Delay to simulate condition change
            update_msg = Message(to="occupant@localhost")
            update_msg.body = "ExitBlocked: Exit A is now blocked"
            await self.send(update_msg)
            print("BMS: Sent update about blocked exit to Occupant.")

    async def setup(self):
        print("BMS agent started...")
        self.add_behaviour(self.EmergencyAlertBehaviour())
        self.add_behaviour(self.ProvideExitInfoBehaviour())
        self.add_behaviour(self.DynamicConditionBehaviour())
