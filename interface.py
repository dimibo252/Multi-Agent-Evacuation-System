import pygame
from building import Building

# Constants for visualization
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_SIZE = 50  # Room size in pixels
SIDEBAR_WIDTH = 300

# Colors for various room types and agents
COLORS = {
    "background": (30, 30, 30),
    "hallway": (200, 200, 200),
    "store": (0, 200, 0),
    "restroom": (200, 200, 0),
    "fire": (255, 0, 0),
    "occupied": (0, 0, 255),
    "normal_exit": (255, 165, 0),
    "emergency_exit": (128, 0, 128),
    "text": (255, 255, 255),
    "sidebar": (50, 50, 50),
    "agent_occupant": (0, 255, 255),  # Cyan for Occupants
    "agent_responder": (255, 0, 0),  # Red for Emergency Responders
}

class PygameInterface:
    def __init__(self, building, agents):
        """
        Initialize the Pygame interface.
        Args:
            building: Instance of the Building class.
            agents: List of agent objects with `location` attributes pointing to a Room.
        """
        self.building = building
        self.agents = agents
        self.current_floor = 0
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Building Emergency Simulation")
        self.font = pygame.font.Font(None, 24)
        self.running = True

    def draw_grid(self):
        """Draw the building layout for the current floor."""
        floor_layout = self.building.layout[self.current_floor]
        for row_index, row in enumerate(floor_layout):
            for col_index, room in enumerate(row):
                if room:
                    # Room rectangle
                    x = col_index * GRID_SIZE
                    y = row_index * GRID_SIZE
                    rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                    color = self.get_room_color(room)
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)  # Grid border

                    # Room type label
                    text_surface = self.font.render(room.room_type, True, COLORS["text"])
                    self.screen.blit(
                        text_surface,
                        (x + GRID_SIZE // 4, y + GRID_SIZE // 4),
                    )

    def draw_agents(self):
        """Draw agents as dots in their current rooms, handling multiple agents per room."""
        agent_positions = {"occupants": {}, "responders": {}}  # Dictionary to track agents by type

        # Group agents by their types and locations (rooms)
        for agent in self.agents:
            if agent.location and agent.location.floor == self.current_floor:
                floor = agent.location.floor
                row = agent.location.row
                col = agent.location.col
                key = (row, col)
                if isinstance(agent, OccupantAgent):
                    agent_positions["occupants"].setdefault(key, []).append(agent)
                elif isinstance(agent, EmergencyResponderAgent):
                    agent_positions["responders"].setdefault(key, []).append(agent)

        # Draw Occupant agents as dots
        for (row, col), agents in agent_positions["occupants"].items():
            x = col * GRID_SIZE + GRID_SIZE // 2
            y = row * GRID_SIZE + GRID_SIZE // 2

            # Spread out dots slightly for multiple agents in the same room
            for index, agent in enumerate(agents):
                offset_x = (index % 3 - 1) * GRID_SIZE // 6  # Offset in X direction
                offset_y = (index // 3 - 1) * GRID_SIZE // 6  # Offset in Y direction
                pygame.draw.circle(self.screen, COLORS["agent_occupant"], (x + offset_x, y + offset_y), GRID_SIZE // 8)

        # Draw Emergency Responder agents as dots
        for (row, col), agents in agent_positions["responders"].items():
            x = col * GRID_SIZE + GRID_SIZE // 2
            y = row * GRID_SIZE + GRID_SIZE // 2

            # Spread out dots slightly for multiple agents in the same room
            for index, agent in enumerate(agents):
                offset_x = (index % 3 - 1) * GRID_SIZE // 6  # Offset in X direction
                offset_y = (index // 3 - 1) * GRID_SIZE // 6  # Offset in Y direction
                pygame.draw.circle(self.screen, COLORS["agent_responder"], (x + offset_x, y + offset_y), GRID_SIZE // 8)

    def draw_sidebar(self):
        """Draw the sidebar with controls and information."""
        sidebar_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLORS["sidebar"], sidebar_rect)

        # Floor buttons
        for i in range(self.building.floors):
            button_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH + 20, 20 + i * 50, 100, 30)
            pygame.draw.rect(self.screen, COLORS["hallway"], button_rect)
            text_surface = self.font.render(f"Floor {i}", True, COLORS["text"])
            self.screen.blit(text_surface, (button_rect.x + 10, button_rect.y + 5))

        # Placeholder for messages
        message_surface = self.font.render("Agent Messages:", True, COLORS["text"])
        self.screen.blit(message_surface, (WINDOW_WIDTH - SIDEBAR_WIDTH + 20, 200))

        # Placeholder for performance metrics
        metrics_surface = self.font.render("Performance Metrics:", True, COLORS["text"])
        self.screen.blit(metrics_surface, (WINDOW_WIDTH - SIDEBAR_WIDTH + 20, 400))

    def get_room_color(self, room):
        """Get the color for a room based on its type or state."""
        if room.fire:
            return COLORS["fire"]
        elif room.is_occupied:
            return COLORS["occupied"]
        elif room.room_type == "H":
            return COLORS["hallway"]
        elif room.room_type == "S":
            return COLORS["store"]
        elif room.room_type == "R":
            return COLORS["restroom"]
        elif room.room_type == "N":
            return COLORS["normal_exit"]
        elif room.room_type == "E":
            return COLORS["emergency_exit"]
        return COLORS["background"]

    def update(self):
        """Main update loop for the interface."""
        self.screen.fill(COLORS["background"])
        self.draw_grid()
        self.draw_agents()
        self.draw_sidebar()
        pygame.display.flip()

    def run(self):
        """Run the Pygame interface."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle floor button clicks
                    x, y = event.pos
                    if x > WINDOW_WIDTH - SIDEBAR_WIDTH:
                        self.handle_sidebar_click(x, y)

            self.update()
        pygame.quit()

    def handle_sidebar_click(self, x, y):
        """Handle clicks on the sidebar."""
        for i in range(self.building.floors):
            if 20 + i * 50 <= y <= 50 + i * 50:
                self.current_floor = i
                break


# Example Usage
class OccupantAgent:
    def __init__(self, name, location):
        self.name = name
        self.location = location  # Location is now a Room object

class EmergencyResponderAgent:
    def __init__(self, name, location):
        self.name = name
        self.location = location  # Location is now a Room object

if __name__ == "__main__":
    # Create a sample building
    building = Building(floors=3, rows=5, cols=5, building_type="shopping_mall")

    # Create mock agents with Room object location
    agents = [
        OccupantAgent("occupant1", building.layout[0][2][2]),  # On floor 0, Room (2,2)
        EmergencyResponderAgent("responder1", building.layout[1][3][4]),  # On floor 1, Room (3,4)
        OccupantAgent("occupant2", building.layout[2][1][1]),  # On floor 2, Room (1,1)
    ]

    # Create and start the interface
    interface = PygameInterface(building, agents)
    interface.run()
