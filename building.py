import random
from collections import deque


class Room:
    def __init__(self, room_type, row, col, floor):
        self.room_type = room_type  # H (Hallway), S (Store), R (Restroom)
        self.row = row
        self.col = col
        self.floor = floor
        self.connections = []  # Rooms that agents can travel through from this one
        self.elevators = []  # Elevator connections to other floors
        self.staircases = [] # Staircase connections to other floors
        self.emergency_staircases = []
        self.fire = False
        self.unavailable = False #for earthquakes or security threath, for example
        self.is_occupied = False 

    def security_threath(self):
        self.unavailable=True
            
    def earthquake(self):
        if random.random( ) < 0.5: #50% of getting damaged because there are earthquakes stronger than others
            self.unvailable = True
            
    def fires(self):
        self.fire = True
        for connection in self.connections:
            if random.random() < 0.05: #5% chance of fire in each connection
                connection.fires()
                
    def connection(self, to_room):
        self.connections.append(to_room)

    def elevator(self, to_room):
        self.elevators.append(to_room)

    def stairs(self, to_room, is_emergency):
        if is_emergency:
            self.emergency_staircases.append(to_room)
        else:
            self.staircases.append(to_room)
    
class Building:
    def __init__(self, floors, rows, cols, building_type="shopping_mall"):
        self.floors = floors
        self.rows = rows
        self.cols = cols
        self.building_type = building_type
        self.layout = self.generate_building_layout()
        self.add_vertical_connections()
        self.add_exits_and_connections()
        self.update_room_connections()
        self.lock_doors = False
        self.lock_elevators = False
        self.lock_communications = False

    def generate_building_layout(self):
        layout = []
        for floor in range(self.floors):
            floor_layout = [[None for _ in range(self.cols)] for _ in range(self.rows)]
            self.place_rooms(floor_layout,floor)
            layout.append(floor_layout)
        return layout

    def place_rooms(self, floor_layout,floor):
        for i in range(self.rows):
            for j in range(self.cols):
                random_number=random.random()
                if random_number < 0.6:  # 60% chance for Hallway
                    floor_layout[i][j] = Room("H", i, j,floor)
                elif random_number < 0.9:  # 30% chance for Store
                    floor_layout[i][j] = Room("S", i, j,floor)
                else:  # 10% chance for Restroom
                    floor_layout[i][j] = Room("R", i, j,floor)

        self.ensure_store_restroom_access(floor_layout,floor)
        self.ensure_hallway_connectivity(floor_layout,floor)

    def ensure_hallway_connectivity(self, floor_layout,floor):
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
                floor_layout[r1][c1] = Room("H", r1, c1, floor)

            # Merge the connected component into the largest component
            largest_component.update(closest_component)
            connected_components.remove(closest_component)

    def ensure_store_restroom_access(self, floor_layout, floor):
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
                        # Try to add a hallway next to it
                        added_hallway = False
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = i + dx, j + dy
                            if (
                                0 <= nx < self.rows
                                and 0 <= ny < self.cols
                                and floor_layout[nx][ny] is None
                            ):
                                floor_layout[nx][ny] = Room("H", nx, ny, floor)
                                added_hallway = True
                                break

                        # If no empty space, replace an adjacent non-hallway room
                        if not added_hallway:
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nx, ny = i + dx, j + dy
                                if (
                                    0 <= nx < self.rows
                                    and 0 <= ny < self.cols
                                    and floor_layout[nx][ny]
                                    and floor_layout[nx][ny].room_type in {"S", "R"}
                                ):
                                    floor_layout[nx][ny] = Room("H", nx, ny, floor)
                                    break


    def add_vertical_connections(self):
        """
        Adds normal stairs, emergency stairs, and elevators connecting all floors.
        - Normal stairs are unique per floor.
        - Emergency stairs are fixed in the same position across all floors.
        - Elevators allow movement between any two floors.
        """
        # Position for emergency stairs (fixed across floors)
        emergency_stair_pos = None
        elevator_pos=None

        for floor_index in range(self.floors - 1):
            current_floor = self.layout[floor_index]
            next_floor = self.layout[floor_index + 1]

            # Find eligible positions for normal stairs
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
                raise ValueError(f"No valid hallway positions for vertical connections on floor {floor_index}")

            # Select positions for normal stairs and emergency stairs
            normal_stair_pos = random.choice(eligible_positions)
            if emergency_stair_pos is None:
                emergency_stair_pos = random.choice(eligible_positions)
            if elevator_pos is None:
                elevator_pos = random.choice(eligible_positions)
                

            # Create and connect normal stairs
            current_normal_stair = current_floor[normal_stair_pos[0]][normal_stair_pos[1]]
            next_normal_stair = next_floor[normal_stair_pos[0]][normal_stair_pos[1]]
            current_normal_stair.stairs(next_normal_stair, is_emergency=False)
            next_normal_stair.stairs(current_normal_stair, is_emergency=False)

            # Create and connect emergency stairs
            current_emergency_stair = current_floor[emergency_stair_pos[0]][emergency_stair_pos[1]]
            next_emergency_stair = next_floor[emergency_stair_pos[0]][emergency_stair_pos[1]]
            current_emergency_stair.stairs(next_emergency_stair, is_emergency=True)
            next_emergency_stair.stairs(current_emergency_stair, is_emergency=True)

            # Add elevators (connect every floor)
            current_elevator = current_floor[elevator_pos[0]][elevator_pos[1]]
            next_elevator = next_floor[elevator_pos[0]][elevator_pos[1]]
            current_elevator.elevator(next_elevator)
            next_elevator.elevator(current_elevator)

    def add_exits_and_connections(self):
        """
        Adds normal and emergency exits on the ground floor.
        Ensures that emergency stairs connect directly to the emergency exit.
        """
        ground_floor = self.layout[0]

        # Find eligible positions for exits
        eligible_positions = [
            (i, j)
            for i in [0, self.rows - 1]
            for j in range(self.cols)
            if ground_floor[i][j] and ground_floor[i][j].room_type == "H"
        ] + [
            (i, j)
            for i in range(self.rows)
            for j in [0, self.cols - 1]
            if ground_floor[i][j] and ground_floor[i][j].room_type == "H"
        ]

        if len(eligible_positions) < 3:
            raise ValueError("Not enough eligible positions for exits.")

        # Select positions for exits
        normal_exit_pos = random.sample(eligible_positions, 2)
        emergency_exit_pos = random.choice(eligible_positions)

        # Place exits on the ground floor
        for pos in normal_exit_pos:
            self.layout[0][pos[0]][pos[1]].room_type = "N"  # Normal exit

        self.layout[0][emergency_exit_pos[0]][emergency_exit_pos[1]].room_type = "E"  # Emergency exit


    def update_room_connections(self):
        for floor_layout in self.layout:
            for i in range(self.rows):
                for j in range(self.cols):
                    room = floor_layout[i][j]
                    if room:
                        # Check adjacent rooms
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = i + dx, j + dy
                            if 0 <= nx < self.rows and 0 <= ny < self.cols:
                                neighbor = floor_layout[nx][ny]
                                if neighbor:
                                    if room.room_type == "H" or "E" or "N":  # Hallway
                                        room.connection(neighbor)
                                    elif neighbor.room_type == "H":  # Store/Restroom to Hallway
                                        room.connection(neighbor)

    def display_building(self):
        for floor_index, floor_layout in enumerate(self.layout):
            print(f"\n--- Floor {floor_index} ---")
            for row in floor_layout:
                print(" ".join(room.room_type if room else "." for room in row))

            print("\nElevators:")
            for row in floor_layout:
                for room in row:
                    if room and room.elevators:
                        connected_floors = [f.floor for f in room.elevators]
                        print(f"  Room ({room.row}, {room.col}) -> Connected floors: {connected_floors}")

            print("\nEmegerncy_Staircases:")
            for row in floor_layout:
                for room in row:
                    if room and room.emergency_staircases:
                        connected_floors = "Emergency"
                        print(f"  Room ({room.row}, {room.col}) -> Stair types: {connected_floors}")

            print("\nStaircases:")
            for row in floor_layout:
                for room in row:
                    if room and room.staircases:
                        connected_floors = "Normal"
                        print(f"  Room ({room.row}, {room.col}) -> Stair types: {connected_floors}")


            if floor_index == 0:  # Show exits only on the ground floor
                print("\nExits:")
                for row in floor_layout:
                    for room in row:
                        if room and room.room_type in {"N", "E"}:
                            exit_type = "Normal" if room.room_type == "N" else "Emergency"
                            print(f"  Exit ({room.row}, {room.col}) -> {exit_type}")


# Example usage
building = Building(floors=3, rows=5, cols=5)
building.display_building()
room=building.layout[0][0][0]
print(room.connections)
