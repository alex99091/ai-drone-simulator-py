from core.drone import Drone

class DroneTracker:
    def __init__(self):
        self.drone = Drone(x=320)  # Initial center position

    def update(self, target_x):
        self.drone.move_towards(target_x)

    def get_position(self):
        return self.drone.get_position()

    def reset(self, position=320):
        self.drone = Drone(x=position)