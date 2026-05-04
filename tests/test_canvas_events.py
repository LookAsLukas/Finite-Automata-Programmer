import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from unittest.mock import MagicMock, patch

import canvas_events
from application_state import EditorMode
from linal import Vector2D
from graph import Node, Transition


class DummyEvent:
    """Вспомогательный класс для имитации событий мыши/тача"""
    def __init__(self, x, y):
        self.local_x = x
        self.local_y = y


@pytest.fixture
def mock_app():
    """Фикстура для создания мока объекта Application с настройками по умолчанию"""
    app = MagicMock()
    
    # Настройки канваса и узлов
    app.attr.canvas_width = 800
    app.attr.canvas_height = 600
    app.config.node_radius = 20
    
    # Состояние графа
    app.graph.node_counter = 0
    app.graph.nodes = set()
    app.graph.transitions = set()
    app.graph.selected_node = None
    app.graph.selected_transition = None
    app.graph.dragging_node = None
    
    # Алфавит
    app.attr.alphabet = set()
    
    return app


def test_event_point():
    e = DummyEvent(150, 250)
    point = canvas_events._event_point(e)
    assert point.x == 150
    assert point.y == 250


@pytest.mark.parametrize("x, y, expected", [
    (100, 100, True),    # Внутри
    (0, 0, True),        # На границе
    (800, 600, True),    # На границе
    (-10, 100, False),   # Слева за пределами
    (100, -10, False),   # Сверху за пределами
    (801, 100, False),   # Справа за пределами
    (100, 601, False),   # Снизу за пределами
])
def test_is_inside_canvas(mock_app, x, y, expected):
    point = Vector2D(x, y)
    assert canvas_events._is_inside_canvas(point, mock_app) == expected


@patch('canvas_events.draw_nodes')
def test_add_node_wrong_mode(mock_draw, mock_app):
    mock_app.attr.editor_mode = EditorMode.SELECT
    canvas_events.add_node(Vector2D(100, 100), mock_app)
    
    mock_app.history.add.assert_not_called()
    assert len(mock_app.graph.nodes) == 0


@patch('canvas_events.draw_nodes')
def test_add_node_too_close_to_edge(mock_draw, mock_app):
    mock_app.attr.editor_mode = EditorMode.NODES
    
    # Клик слишком близко к левому краю (x < 20)
    canvas_events.add_node(Vector2D(10, 100), mock_app)
    mock_app.history.add.assert_not_called()
    assert len(mock_app.graph.nodes) == 0


@patch('canvas_events.draw_nodes')
def test_add_node_success(mock_draw, mock_app):
    mock_app.attr.editor_mode = EditorMode.NODES
    
    canvas_events.add_node(Vector2D(100, 100), mock_app)
    
    mock_app.history.add.assert_called_once_with(mock_app.graph)
    assert len(mock_app.graph.nodes) == 1
    assert mock_app.graph.node_counter == 1
    
    added_node = next(iter(mock_app.graph.nodes))
    assert added_node.name == "q0"
    assert added_node.x == 100
    assert added_node.y == 100
    
    mock_draw.assert_called_once_with(mock_app)


@patch('canvas_events.get_clicked_node')
@patch('canvas_events.get_clicked_transition')
@patch('canvas_events.draw_nodes')
def test_handle_canvas_click_add_transition(mock_draw, mock_get_transition, mock_get_node, mock_app):
    mock_app.attr.editor_mode = EditorMode.TRANSITIONS
    mock_app.attr.alphabet = {"b"}  # Тестируем выбор символа
    
    node1 = Node(x=10, y=10, name="q0")
    node2 = Node(x=50, y=50, name="q1")
    mock_app.graph.selected_node = node1
    
    mock_get_node.return_value = node2
    mock_get_transition.return_value = None
    
    e = DummyEvent(50, 50)
    canvas_events.handle_canvas_click(e, mock_app)
    
    assert len(mock_app.graph.transitions) == 1
    transition = next(iter(mock_app.graph.transitions))
    assert transition.start == node1
    assert transition.end == node2
    assert transition.symbols == "b"
    
    assert mock_app.graph.selected_node == node2
    mock_draw.assert_called_once()


@patch('canvas_events.get_clicked_node')
@patch('canvas_events.rename_state_dialog')
def test_handle_double_click_on_node(mock_dialog, mock_get_node, mock_app):
    mock_app.attr.editor_mode = EditorMode.SELECT
    
    clicked_node = Node(x=100, y=100, name="q0")
    mock_get_node.return_value = clicked_node
    mock_dialog.return_value = "mock_dialog_obj"
    
    e = DummyEvent(100, 100)
    canvas_events.handle_double_click(e, mock_app)
    
    mock_dialog.assert_called_once_with(clicked_node, mock_app)
    mock_app.page.open.assert_called_once_with("mock_dialog_obj")


@patch('canvas_events.get_clicked_node')
@patch('canvas_events.draw_nodes')
def test_handle_drag_start(mock_draw, mock_get_node, mock_app):
    mock_app.attr.editor_mode = EditorMode.SELECT
    
    dragged_node = Node(x=100, y=100, name="q0")
    mock_get_node.return_value = dragged_node
    
    e = DummyEvent(100, 100)
    canvas_events.handle_drag_start(e, mock_app)
    
    assert mock_app.graph.dragging_node == dragged_node
    mock_app.history.add.assert_called_once_with(mock_app.graph)
    mock_draw.assert_called_once_with(mock_app)


def test_handle_drag_update_with_clamping(mock_app):
    dragged_node = Node(x=100, y=100, name="q0")
    mock_app.graph.dragging_node = dragged_node
    
    # Пытаемся вытащить узел за границы (x=-50, y=1000)
    e = DummyEvent(-50, 1000)
    
    with patch('canvas_events.draw_nodes') as mock_draw:
        canvas_events.handle_drag_update(e, mock_app)
        
        # Узел должен быть ограничен рамками (node_radius до canvas_width/height - node_radius)
        assert dragged_node.x == 20   # min(max(-50, 20), 800) -> 20
        assert dragged_node.y == 580  # min(max(1000, 20), 580) -> 580
        
        mock_draw.assert_called_once_with(mock_app)
        mock_app.page.update.assert_called_once()


def test_handle_drag_end(mock_app):
    dragged_node = Node(x=100, y=100, name="q0")
    mock_app.graph.dragging_node = dragged_node
    
    e = DummyEvent(100, 100)
    canvas_events.handle_drag_end(e, mock_app)
    
    assert mock_app.graph.dragging_node is None
    mock_app.page.update.assert_called_once()