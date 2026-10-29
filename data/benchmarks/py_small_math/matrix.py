"""Matrix transformation module."""
from vector import Vector2D, dot_product

class Matrix2x2:
    """Represents a 2x2 matrix."""
    def __init__(self, a: float, b: float, c: float, d: float):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def determinant(self) -> float:
        return self.a * self.d - self.b * self.c

    def transform(self, v: Vector2D) -> Vector2D:
        return Vector2D(self.a * v.x + self.b * v.y, self.c * v.x + self.d * v.y)
