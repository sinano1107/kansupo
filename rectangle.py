import random


class Rectangle:
    def __init__(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        self.X_RANGE = x_range
        self.Y_RANGE = y_range
    
    def randam_point(self):
        x = random.uniform(self.X_RANGE[0], self.X_RANGE[1])
        y = random.uniform(self.Y_RANGE[0], self.Y_RANGE[1])
        return (x, y)