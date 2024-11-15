class Building:
    def __init__(self, layout):
        """
        Initialize the building with a layout.
        :param layout: A dictionary representing the building layout (nodes, connections).
        :param floors: Total number of floors in the building. If not in layout with as a default number.
        """
        self.layout = layout["nodes"]
        if layout["flores"]:
            self.floors = layout["floors"]
        else:
            self.floors=1

    def set_node_status(self, node, status_type, status_value):
        """
        Set the status of a specific node (e.g., marking it as 'fire').
        :param node: The name of the node (e.g., 'Store A').
        :param status_type: The type of status to change (e.g., 'type', 'accessible').
        :param status_value: The value to set for the given status type (e.g., 'Fire').
        """
        if node in self.layout:
            self.layout[node][status_type] = status_value
        else:
            print(f"Node '{node}' does not exist in the building.")

    def get_node_info(self, node):
        """
        Retrieve information about a specific node.
        :param node: The name of the node (e.g., 'Store A').
        :return: A dictionary with the node's information.
        """
        return self.layout.get(node, f"Node '{node}' does not exist.")

    def find_connected_nodes(self, node):
        """
        Get a list of nodes connected to the given node.
        :param node: The name of the node (e.g., 'Store A').
        :return: A list of connected nodes or a message if the node doesn't exist.
        """
        if node in self.layout:
            return self.layout[node].get("connected_to", [])
        else:
            return f"Node '{node}' does not exist."

    def is_accessible(self, node):
        """
        Check if a node is accessible.
        :param node: The name of the node (e.g., 'Store A').
        :return: Boolean indicating if the node is accessible.
        """
        return self.layout.get(node, {}).get("accessible", False)

    def display_building(self):
        """
        Display the current building layout.
        """
        import pprint
        pprint.pprint(self.layout)


# Example Usage
building_data = {
    "nodes": {
        # Floor 1
        "Entrance 1": {"type": "Entrance", "accessible": True, "floor": 1, "connected_to": ["Lobby"]},
        "Entrance 2": {"type": "Entrance", "accessible": True, "floor": 1, "connected_to": ["Lobby"]},
        "Lobby": {"type": "Lobby", "accessible": True, "floor": 1, "connected_to": ["Entrance 1", "Entrance 2", "Store 1", "Store 2", "Walkway 1", "Elevator 1", "Stairs 1"]},
        "Store 1": {"type": "Store", "accessible": True, "floor": 1, "connected_to": ["Lobby", "Walkway 1"]},
        "Store 2": {"type": "Store", "accessible": True, "floor": 1, "connected_to": ["Lobby", "Walkway 1"]},
        "Walkway 1": {"type": "Walkway", "accessible": True, "floor": 1, "connected_to": ["Store 1", "Store 2", "Lobby", "Emergency Exit 1"]},
        "Emergency Exit 1": {"type": "Exit", "accessible": True, "floor": 1, "connected_to": ["Walkway 1"]},
        "Elevator 1": {"type": "Elevator", "accessible": True, "floor": 1, "connected_to": ["Lobby", "Floor 2 Elevator 1"]},
        "Stairs 1": {"type": "Stairs", "accessible": True, "floor": 1, "connected_to": ["Lobby", "Floor 2 Stairs 1"]},

        # Floor 2
        "Floor 2 Elevator 1": {"type": "Elevator", "accessible": True, "floor": 2, "connected_to": ["Elevator 1", "Floor 2 Walkway"]},
        "Floor 2 Stairs 1": {"type": "Stairs", "accessible": True, "floor": 2, "connected_to": ["Stairs 1", "Floor 2 Walkway"]},
        "Floor 2 Walkway": {"type": "Walkway", "accessible": True, "floor": 2, "connected_to": ["Floor 2 Elevator 1", "Floor 2 Stairs 1", "Store 3", "Store 4", "Emergency Exit 2"]},
        "Store 3": {"type": "Store", "accessible": True, "floor": 2, "connected_to": ["Floor 2 Walkway"]},
        "Store 4": {"type": "Store", "accessible": True, "floor": 2, "connected_to": ["Floor 2 Walkway"]},
        "Emergency Exit 2": {"type": "Exit", "accessible": True, "floor": 2, "connected_to": ["Floor 2 Walkway"]},
    },
    "floors": 2,
}
