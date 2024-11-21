import random

class Emergency:
    def __init__(self, building, emergency_type=None):
        self.building = building
        if emergency_type is None:
            self.emergency_type = self.get_emergency()
        else:
            self.emergency_type=emergency_type
        self.initiate_emergency()
    
    def get_emergency(self):
        random_number=random.random()
        if random_number < 0.25:
            emergency_type = "Fire"
        elif random_number < 0.5:
            emergency_type = "Earthquake"
        elif random_number < 0.75:
            emergency_type = "Security Threath" #attacks
        else:
            emergency_type = "Security Breach" #gas leaks and those types of problems
        return emergency_type

    def initiate_emergency(self):
        if self.emergency_type == "Fire":
            pass
        if self.emergency_type == "Earthquake":
            pass
        if self.emergency_type == "Security Threath":
            pass
        if self.emergency_type == "Security Breach":
            pass
            