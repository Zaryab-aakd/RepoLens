"""Vector operations module."""
import math

class Vector2D:
    """Represents a 2D vector."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

def dot_product(v1: Vector2D, v2: Vector2D) -> float:
    return v1.x * v2.x + v1.y * v2.y
