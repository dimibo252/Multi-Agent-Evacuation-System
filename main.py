from Agents.OccupantAgent import OccupantAgent
from Agents.BMSAgent import BMSAgent
from Agents.EmergencyResponderAgent import EmergencyResponderAgent
import asyncio
import random
import building

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
                password="password",
                agent_name=f"Agent {i}",
                condition=condition,
                building=building,
            )
            # Verifica se a localização é única
            if agent.location not in occupied_locations:
                occupied_locations.add(agent.location)
                occupant_agents.append(agent)
                break
    cop_agent = EmergencyResponderAgent("cop@localhost", "isiapassword", role="cop")
    fireman_agent = EmergencyResponderAgent("fireman@localhost", "isiapassword", role="fireman")
    bms_agent = BMSAgent("bms@localhost", "isiapassword",num_occupants, "BMS Agent")

    for agent in occupant_agents:
        building.add_agent(agent)
    building.add_emergency_agent(cop_agent)
    building.add_emergency_agent(fireman_agent)
    building.add_bms_agent(bms_agent)
   

    for agent in occupant_agents:
        await agent.start()
    await cop_agent.start()
    await fireman_agent.start()
    await bms_agent.start()

    await asyncio.sleep(40) 

    for agent in occupant_agents:
        await agent.stop()
    await cop_agent.stop()
    await fireman_agent.stop()
    await bms_agent.stop()
    await bms_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
