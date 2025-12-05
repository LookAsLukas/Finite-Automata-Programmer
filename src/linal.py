from dataclasses import dataclass
from math import sqrt, atan2, sin, cos


@dataclass
class Vector2D:
    x: float
    y: float

    def phi(self):
        return atan2(self.y, self.x)

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        return Vector2D(self.x, self.y) / self.length()

    def turned(self, radians):
        new_phi = self.phi() + radians
        length = self.length()
        return Vector2D(length * cos(new_phi), length * sin(new_phi))

    def perpendicular(self):
        return Vector2D(-self.y, self.x)

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            raise TypeError("Vector2D addition with non-Vector2D is undefined")
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vector2D):
            raise TypeError("Vector2D subtraction with non-Vector2D is undefined")
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise TypeError("Vector2D multiplication with non-number is undefined")
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise TypeError("Vector2D true division with non-number is undefined")
        return Vector2D(self.x / scalar, self.y / scalar)


def dot_product(v1: Vector2D, v2: Vector2D) -> float:
    return v1.x * v2.x + v1.y * v2.y

