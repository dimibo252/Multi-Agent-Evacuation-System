import random
from collections import deque


class Room:
    def __init__(self, room_type, row, col):
        self.room_type = room_type  # H (Hallway), S (Store), R (Restroom)
        self.row = row
        self.col = col
        self.connections = []  # Rooms that agents can travel through from this one
        self.elevators = []  # Elevator connections to other floors
        self.staircases = []  # Staircase connections to other floors

    def connection(self, to_room):
        self.connections.append(to_room)

    def elevator(self, to_room):
        self.elevators.append(to_room)

    def stairs(self, to_room):
        self.staircases.append(to_room)

class Building:
    def __init__(self, floors, rows, cols, building_type="shopping_mall"):
        self.floors = floors
        self.rows = rows
        self.cols = cols
        self.building_type = building_type
        self.layout = self.generate_building_layout()
        self.add_vertical_connections()
        self.validate_layout()

    def generate_building_layout(self):
        layout = []
        for floor in range(self.floors):
            floor_layout = [[None for _ in range(self.cols)] for _ in range(self.rows)]
            self.place_rooms(floor_layout)
            layout.append(floor_layout)
        return layout

    def place_rooms(self, floor_layout):
        for i in range(self.rows):
            for j in range(self.cols):
                if random.random() < 0.6:  # 60% chance for Hallway
                    floor_layout[i][j] = Room("H", i, j)
                elif random.random() < 0.9:  # 30% chance for Store
                    floor_layout[i][j] = Room("S", i, j)
                else:  # 10% chance for Restroom
                    floor_layout[i][j] = Room("R", i, j)

        self.ensure_store_restroom_access(floor_layout)
        self.ensure_hallway_connectivity(floor_layout)

    def ensure_hallway_connectivity(self, floor_layout):
        """
        Ensures all hallway ('H') tiles on a floor are connected.
        Any hallway tile must be reachable from any other hallway tile.
        """
        rows = len(floor_layout)
        cols = len(floor_layout[0])

        # Helper: Find all connected hallways using BFS
        def find_connected_hallways(start):
            visited = set()
            queue = deque([start])
            while queue:
                r, c = queue.popleft()
                if (r, c) in visited:
                    continue
                visited.add((r, c))
                # Explore neighbors
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < rows
                        and 0 <= nc < cols
                        and floor_layout[nr][nc]
                        and floor_layout[nr][nc].room_type == "H"
                        and (nr, nc) not in visited
                    ):
                        queue.append((nr, nc))
            return visited

        # Find all hallway tiles
        hallway_positions = [
            (r, c) for r in range(rows) for c in range(cols) if floor_layout[r][c] and floor_layout[r][c].room_type == "H"
        ]
        if not hallway_positions:
            return  # No hallways to connect

        # Find all connected components
        connected_components = []
        unvisited = set(hallway_positions)
        while unvisited:
            start = next(iter(unvisited))  # Get any unvisited hallway tile
            component = find_connected_hallways(start)
            connected_components.append(component)
            unvisited -= component

        # If there's only one connected component, we're done
        if len(connected_components) == 1:
            return

        # Otherwise, connect the components
        largest_component = connected_components.pop(0)  # Start with the largest (or first) component
        while connected_components:
            # Find the closest component to the largest component
            closest_component = None
            closest_pair = None
            min_distance = float("inf")

            for component in connected_components:
                for r1, c1 in largest_component:
                    for r2, c2 in component:
                        distance = abs(r1 - r2) + abs(c1 - c2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_pair = ((r1, c1), (r2, c2))
                            closest_component = component

            # Connect the two components
            (r1, c1), (r2, c2) = closest_pair
            while (r1, c1) != (r2, c2):
                if r1 < r2:
                    r1 += 1
                elif r1 > r2:
                    r1 -= 1
                elif c1 < c2:
                    c1 += 1
                elif c1 > c2:
                    c1 -= 1
                floor_layout[r1][c1] = Room("H", r1, c1)

            # Merge the connected component into the largest component
            largest_component.update(closest_component)
            connected_components.remove(closest_component)

    def ensure_store_restroom_access(self, floor_layout):
        """
        Ensures every store ('S') and restroom ('R') is adjacent to at least one hallway ('H').
        """
        for i in range(self.rows):
            for j in range(self.cols):
                room = floor_layout[i][j]
                if room and room.room_type in {"S", "R"}:
                    # Check if adjacent to a hallway
                    connected_to_hallway = any(
                        0 <= i + dx < self.rows and 0 <= j + dy < self.cols and
                        floor_layout[i + dx][j + dy] and
                        floor_layout[i + dx][j + dy].room_type == "H"
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    )
                    if not connected_to_hallway:
                        # Add a hallway next to it
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = i + dx, j + dy
                            if (
                                0 <= nx < self.rows
                                and 0 <= ny < self.cols
                                and floor_layout[nx][ny] is None
                            ):
                                floor_layout[nx][ny] = Room("H", nx, ny)
                                break


    def add_vertical_connections(self):
        for floor_index in range(self.floors - 1):
            current_floor = self.layout[floor_index]
            next_floor = self.layout[floor_index + 1]

            eligible_positions = [
                (i, j)
                for i in [0, self.rows - 1]
                for j in range(self.cols)
                if current_floor[i][j] and current_floor[i][j].room_type == "H"
            ] + [
                (i, j)
                for i in range(self.rows)
                for j in [0, self.cols - 1]
                if current_floor[i][j] and current_floor[i][j].room_type == "H"
            ]

            if not eligible_positions:
                raise ValueError(f"No valid hallway positions for elevators/stairs on floor {floor_index}")

            elevator_pos = random.choice(eligible_positions)
            staircase_pos = random.choice(eligible_positions)

            current_elevator_room = current_floor[elevator_pos[0]][elevator_pos[1]]
            next_elevator_room = next_floor[elevator_pos[0]][elevator_pos[1]]
            current_elevator_room.elevator(next_elevator_room)
            next_elevator_room.elevator(current_elevator_room)

            current_staircase_room = current_floor[staircase_pos[0]][staircase_pos[1]]
            next_staircase_room = next_floor[staircase_pos[0]][staircase_pos[1]]
            current_staircase_room.stairs(next_staircase_room)
            next_staircase_room.stairs(current_staircase_room)

    def validate_layout(self):
        for floor_layout in self.layout:
            self.ensure_hallway_connectivity(floor_layout)

    def display_building(self):
        for floor_index, floor_layout in enumerate(self.layout):
            print(f"Floor {floor_index}:")
            for row in floor_layout:
                print(" ".join(room.room_type if room else "." for room in row))
            print()

            # Indicate elevators and staircases
            print("Elevators:")
            for row in floor_layout:
                for room in row:
                    if room and room.elevators:
                        print(f"  Room at ({room.row}, {room.col}) -> Elevator to floors: {[f.row for f in room.elevators]}")

            print("Staircases:")
            for row in floor_layout:
                for room in row:
                    if room and room.staircases:
                        print(f"  Room at ({room.row}, {room.col}) -> Stairs to floors: {[f.row for f in room.staircases]}")


# Example usage
building = Building(floors=3, rows=5, cols=5)
building.display_building()
