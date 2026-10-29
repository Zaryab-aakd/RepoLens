"""Entrypoint for py_small_math."""
from vector import Vector2D, dot_product
from matrix import Matrix2x2

def run_math_pipeline(scale: float) -> float:
    v = Vector2D(3.0, 4.0)
    m = Matrix2x2(scale, 0, 0, scale)
    v_transformed = m.transform(v)
    return v_transformed.magnitude()
