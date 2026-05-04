import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from unittest.mock import MagicMock, patch
import flet as ft
from flet import canvas

import draw
from graph import NodeType
from linal import Vector2D


@pytest.fixture
def mock_app():
    app = MagicMock()
    app.config.node_radius = 20
    app.config.start_final_node_color = "#111111"
    app.config.start_node_color = "#222222"
    app.config.final_node_color = "#333333"
    app.config.node_color = "#444444"
    app.config.selection_color = "#555555"
    
    app.attr.debug_mode = False
    app.attr.current_states = set()
    
    app.graph.nodes = set()
    app.graph.transitions = set()
    app.graph.selected_node = None
    app.graph.selected_transition = None
    
    app.ui.drawing_area.shapes = []
    return app


@patch('draw.calc_transitions', return_value=[])
def test_draw_nodes(mock_calc_transitions, mock_app):
    node_normal = MagicMock(x=10, y=10, type=NodeType.NORMAL, name="q0")
    node_start = MagicMock(x=50, y=50, type=NodeType.START, name="q1")
    node_final = MagicMock(x=90, y=90, type=NodeType.FINAL, name="q2")
    node_start_final = MagicMock(x=130, y=130, type=NodeType.START_FINAL, name="q3")
    
    mock_app.graph.nodes = {node_normal, node_start, node_final, node_start_final}
    
    draw.draw_nodes(mock_app)
    
    assert len(mock_app.ui.drawing_area.shapes) == 8
    mock_app.ui.drawing_area.update.assert_called_once()


@patch('draw.calc_transitions', return_value=[])
def test_draw_nodes_debug_glow(mock_calc_transitions, mock_app):
    node = MagicMock(x=10, y=10, type=NodeType.NORMAL, name="q0")
    mock_app.graph.nodes = {node}
    mock_app.attr.debug_mode = True
    mock_app.attr.current_states = {"q0"}
    
    draw.draw_nodes(mock_app)
    
    assert len(mock_app.ui.drawing_area.shapes) == 2


@patch('draw.calc_transitions', return_value=[])
def test_draw_nodes_selected(mock_calc_transitions, mock_app):
    node = MagicMock(x=10, y=10, type=NodeType.NORMAL, name="q0")
    mock_app.graph.nodes = {node}
    mock_app.graph.selected_node = node
    
    draw.draw_nodes(mock_app)
    
    assert len(mock_app.ui.drawing_area.shapes) == 3


def test_is_line_intersecting_node(mock_app):
    start = Vector2D(0, 0)
    end = Vector2D(100, 0)
    
    node_intersect = MagicMock()
    node_no_intersect = MagicMock()
    
    mock_app.graph.nodes = {node_intersect}
    with patch('linal.Vector2D.from_node', return_value=Vector2D(50, 10)):
        assert draw.is_line_intersecting_node(start, end, mock_app) is True
        
    mock_app.graph.nodes = {node_no_intersect}
    with patch('linal.Vector2D.from_node', return_value=Vector2D(50, 100)):
        assert draw.is_line_intersecting_node(start, end, mock_app) is False


def test_is_line_intersecting_node_zero_length(mock_app):
    start = Vector2D(0, 0)
    end = Vector2D(0, 0)
    assert draw.is_line_intersecting_node(start, end, mock_app) is False


def test_calc_self_line():
    paint = ft.Paint(color="#000000", stroke_width=2)
    point = Vector2D(100, 100)
    elements = draw.calc_self_line("a", paint, point, 20.0, {0.0, math.pi})
    
    assert len(elements) == 4
    assert isinstance(elements[0], canvas.Arc)
    assert isinstance(elements[1], canvas.Line)
    assert isinstance(elements[2], canvas.Line)
    assert isinstance(elements[3], canvas.Text)


def test_calc_curved_line():
    paint = ft.Paint(color="#000000", stroke_width=2)
    start = Vector2D(0, 0)
    end = Vector2D(100, 100)
    elements = draw.calc_curved_line("b", paint, start, end, 20.0)
    
    assert len(elements) == 4
    assert isinstance(elements[0], canvas.Path)
    assert isinstance(elements[1], canvas.Line)
    assert isinstance(elements[2], canvas.Line)
    assert isinstance(elements[3], canvas.Text)


def test_calc_line():
    paint = ft.Paint(color="#000000", stroke_width=2)
    start = Vector2D(0, 0)
    end = Vector2D(100, 100)
    
    elements_single = draw.calc_line("c", paint, start, end, False, 20.0)
    assert len(elements_single) == 4
    assert isinstance(elements_single[0], canvas.Line)
    
    elements_double = draw.calc_line("d", paint, start, end, True, 20.0)
    assert len(elements_double) == 4


@patch('draw.calc_self_line', return_value=[MagicMock()])
@patch('draw.calc_line', return_value=[MagicMock()])
@patch('draw.calc_curved_line', return_value=[MagicMock()])
@patch('draw.is_line_intersecting_node', return_value=False)
@patch('linal.Vector2D.from_transition', return_value=Vector2D(1, 0))
@patch('linal.Vector2D.from_node', return_value=Vector2D(0, 0))
def test_calc_transitions(mock_from_node, mock_from_trans, mock_intersect, mock_curve, mock_line, mock_self, mock_app):
    node1 = MagicMock()
    node2 = MagicMock()
    
    t_self = MagicMock(start=node1, end=node1, symbols="a")
    t_normal = MagicMock(start=node1, end=node2, symbols="b")
    t_double1 = MagicMock(start=node2, end=node1, symbols="c")
    t_double2 = MagicMock(start=node1, end=node2, symbols="d")
    
    mock_app.graph.transitions = {t_self, t_normal, t_double1, t_double2}
    mock_app.graph.selected_transition = t_normal
    
    elements = draw.calc_transitions(mock_app)
    
    assert len(elements) == 4
    mock_self.assert_called()
    mock_line.assert_called()