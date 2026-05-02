import pytest
import sys
import os
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from linal import Vector2D, dot_product

class TestVector2D:
    def test_creation(self):
        v = Vector2D(3, 4)
        assert v.x == 3
        assert v.y == 4

    def test_from_node(self):
        class MockNode:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        node = MockNode(5, 7)
        v = Vector2D.from_node(node)
        assert v.x == 5
        assert v.y == 7

    def test_from_transition(self):
        class MockNode:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        class MockTransition:
            def __init__(self, start, end):
                self.start = start
                self.end = end
        start = MockNode(1, 2)
        end = MockNode(4, 6)
        transition = MockTransition(start, end)
        v = Vector2D.from_transition(transition)
        assert v.x == 3
        assert v.y == 4

    def test_from_phi_r(self):
        v = Vector2D.from_phi_r(math.pi/2, 5)
        assert abs(v.x) < 1e-9
        assert abs(v.y - 5) < 1e-9

        v = Vector2D.from_phi_r(0, 3)
        assert v.x == 3
        assert v.y == 0

    def test_to_tuple(self):
        v = Vector2D(2, -3)
        assert v.to_tuple() == (2, -3)

    def test_phi(self):
        v = Vector2D(1, 0)
        assert v.phi() == 0
        v = Vector2D(0, 1)
        assert v.phi() == math.pi/2
        v = Vector2D(-1, 0)
        assert v.phi() == math.pi
        v = Vector2D(0, -1)
        assert v.phi() == -math.pi/2

    def test_length(self):
        v = Vector2D(3, 4)
        assert v.length() == 5
        v = Vector2D(0, 0)
        assert v.length() == 0

    def test_normalized(self):
        v = Vector2D(3, 4)
        n = v.normalized()
        assert abs(n.length() - 1) < 1e-9
        assert abs(n.x - 0.6) < 1e-9
        assert abs(n.y - 0.8) < 1e-9

        with pytest.raises(ZeroDivisionError):
            Vector2D(0, 0).normalized()

    def test_turned(self):
        v = Vector2D(1, 0)
        v2 = v.turned(math.pi/2)
        assert abs(v2.x) < 1e-9
        assert abs(v2.y - 1) < 1e-9

        v = Vector2D(1, 1)
        v2 = v.turned(math.pi/4)
        expected_len = math.sqrt(2)
        assert abs(v2.x) < 1e-9
        assert abs(v2.y - expected_len) < 1e-9

    def test_perpendicular(self):
        v = Vector2D(2, 3)
        perp = v.perpendicular()
        assert perp.x == -3
        assert perp.y == 2

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

    def test_mul(self):
        v = Vector2D(2, 3)
        v2 = v * 3
        assert v2.x == 6
        assert v2.y == 9

    def test_truediv(self):
        v = Vector2D(6, 9)
        v2 = v / 3
        assert v2.x == 2
        assert v2.y == 3

    def test_neg(self):
        v = Vector2D(1, -2)
        v2 = -v
        assert v2.x == -1
        assert v2.y == 2

    def test_dot_product(self):
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        assert dot_product(v1, v2) == 11
        assert dot_product(v2, v1) == 11