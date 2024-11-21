from Agents.OccupantAgent import OccupantAgent
from Agents.BMSAgent import BMSAgent
from Agents.EmergencyResponderAgent import EmergencyResponderAgent
from Agents.emergency import EmergencyAgent
import asyncio
import random
from building import building  # Ensure this is the correct import


async def main():
    # Número de ocupantes a ser criado
    num_occupants = random.randint(1, 10)
    occupant_agents = []
    occupied_locations = set()
    for i in range(1, num_occupants + 1):
        condition = "functional" if random.random() < 0.84 else "disabled"
        while True:
            # Cria uma sala inicial aleatória
            agent = OccupantAgent(
                jid=f"occupant{i}@localhost",
                password="isiapassword",
                agent_name=f"Agent {i}",
                condition=condition,
                building=building,
            )
            # Verifica se a localização é única
            if agent.location not in occupied_locations:
                occupied_locations.add(agent.location)
                occupant_agents.append(agent)
                break

    # Pass building as an argument to EmergencyResponderAgent and BMSAgent
    cop_agent = EmergencyResponderAgent("cop@localhost", "isiapassword", role="cop", building=building)
    fireman_agent = EmergencyResponderAgent("fireman@localhost", "isiapassword", role="fireman", building=building)

    # Ensure building is passed to BMSAgent
    bms_agent = BMSAgent("bms@localhost", "isiapassword", num_occupants, "BMS Agent", building=building)

    emergency_agent = EmergencyAgent("emergency@localhost", "isiapassword", building)

    # Start all agents
    for agent in occupant_agents:
        await agent.start()
    await cop_agent.start()
    await fireman_agent.start()
    await bms_agent.start()
    await emergency_agent.start()

    await asyncio.sleep(40)

    # Stop all agents after the simulation
    for agent in occupant_agents:
        await agent.stop()
    await cop_agent.stop()
    await fireman_agent.stop()
    await bms_agent.stop()
    await emergency_agent.stop()


if __name__ == "__main__":
    asyncio.run(main())