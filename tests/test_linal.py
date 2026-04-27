import sys
import os
import math
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from linal import Vector2D, dot_product
from graph import Node, Transition


class TestVector2D:
    def test_creation(self):
        v = Vector2D(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_to_tuple(self):
        v = Vector2D(1, -2)
        assert v.to_tuple() == (1, -2)

    def test_add(self):
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        v3 = v1 + v2
        assert v3.x == 4
        assert v3.y == 6

    def test_sub(self):
        v1 = Vector2D(5, 7)
        v2 = Vector2D(2, 3)
        v3 = v1 - v2
        assert v3.x == 3
        assert v3.y == 4

    def test_mul_scalar(self):
        v = Vector2D(2, 3)
        v2 = v * 2.5
        assert v2.x == 5.0
        assert v2.y == 7.5

    def test_truediv_scalar(self):
        v = Vector2D(4, 6)
        v2 = v / 2
        assert v2.x == 2.0
        assert v2.y == 3.0

    def test_neg(self):
        v = Vector2D(1, -2)
        v2 = -v
        assert v2.x == -1
        assert v2.y == 2

    def test_length(self):
        v = Vector2D(3, 4)
        assert v.length() == 5.0
        v0 = Vector2D(0, 0)
        assert v0.length() == 0.0

    def test_normalized(self):
        v = Vector2D(3, 4)
        norm = v.normalized()
        assert norm.length() == pytest.approx(1.0)
        assert norm.x == pytest.approx(3/5)
        assert norm.y == pytest.approx(4/5)

    def test_normalized_zero_vector(self):
        v = Vector2D(0, 0)
        with pytest.raises(ZeroDivisionError):
            _ = v.normalized()

    def test_phi(self):
        assert Vector2D(1, 0).phi() == pytest.approx(0)
        assert Vector2D(0, 1).phi() == pytest.approx(math.pi/2)
        assert Vector2D(-1, 0).phi() == pytest.approx(math.pi)
        assert Vector2D(0, -1).phi() == pytest.approx(-math.pi/2)

    def test_turned(self):
        v = Vector2D(1, 0)
        v90 = v.turned(math.pi/2)
        assert v90.x == pytest.approx(0)
        assert v90.y == pytest.approx(1)
        v360 = v.turned(2*math.pi)
        assert v360.x == pytest.approx(1)
        assert v360.y == pytest.approx(0)

    def test_perpendicular(self):
        v = Vector2D(2, 3)
        perp = v.perpendicular()
        assert perp.x == -3
        assert perp.y == 2
        assert dot_product(v, perp) == 0

    def test_from_phi_r(self):
        v = Vector2D.from_phi_r(0, 5)
        assert v.x == pytest.approx(5)
        assert v.y == pytest.approx(0)
        v = Vector2D.from_phi_r(math.pi/2, 3)
        assert v.x == pytest.approx(0)
        assert v.y == pytest.approx(3)

    def test_from_node(self):
        node = Node(x=10.5, y=20.5, name="q0")
        v = Vector2D.from_node(node)
        assert v.x == 10.5
        assert v.y == 20.5

    def test_from_transition(self):
        start = Node(x=0, y=0, name="A")
        end = Node(x=3, y=4, name="B")
        trans = Transition(start=start, end=end, symbols="a")
        v = Vector2D.from_transition(trans)
        assert v.x == 3
        assert v.y == 4

    def test_dot_product(self):
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        assert dot_product(v1, v2) == 11
        v3 = Vector2D(1, 0)
        v4 = Vector2D(0, 1)
        assert dot_product(v3, v4) == 0