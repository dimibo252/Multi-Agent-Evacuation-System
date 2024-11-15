from OccupantAgent import OccupantAgent
from BMSAgent import BMSAgent
from EmergencyResponderAgent import EmergencyResponderAgent
import asyncio

async def main():
    occupant_agent = OccupantAgent("occupant@localhost", "isiapassword")
    bms_agent = BMSAgent("bms@localhost", "isiapassword")
    responder_agent = EmergencyResponderAgent("responder@localhost", "isiapassword")

    await bms_agent.start()
    await responder_agent.start()
    await asyncio.sleep(1)
    await occupant_agent.start()

    await asyncio.sleep(30)  # Run for 30 seconds for demonstration

    await occupant_agent.stop()
    await bms_agent.stop()
    await responder_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())