import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from unittest.mock import MagicMock, patch
import flet as ft

import edit_events
from application_state import EditorMode, ApplicationState
from graph import NodeType, Graph


@pytest.fixture
def mock_app():
    app = MagicMock()
    app.attr.editor_mode = EditorMode.SELECT
    app.attr.base_canvas_width = 800
    app.attr.base_canvas_height = 600
    app.attr.canvas_width = 800
    app.attr.canvas_height = 600
    app.attr.canvas_scale = 1.0
    app.attr.min_canvas_scale = 0.5
    app.attr.max_canvas_scale = 2.0
    app.attr.canvas_scale_step = 0.1
    app.config.node_radius = 20

    app.graph.nodes = set()
    app.graph.transitions = set()
    app.graph.selected_node = None
    app.graph.selected_transition = None
    app.graph.get_start_states.return_value = set()
    app.graph.get_final_states.return_value = set()

    app.attr.alphabet = set()
    app.ui.alphabet_input.value = ""
    app.ui.status_text.value = ""
    return app


def test_build_mode_button_style():
    style = edit_events._build_mode_button_style("#000000", True)
    assert isinstance(style, ft.ButtonStyle)
    assert style.elevation[ft.ControlState.DEFAULT] == 1

    style_inactive = edit_events._build_mode_button_style("#000000", False)
    assert style_inactive.elevation[ft.ControlState.DEFAULT] == 0


def test_set_mode_button_state_active():
    button = MagicMock()
    edit_events._set_mode_button_state(button, EditorMode.NODES, EditorMode.NODES)
    assert button.bgcolor == "#ffedd5"


def test_set_mode_button_state_inactive():
    button = MagicMock()
    edit_events._set_mode_button_state(button, EditorMode.NODES, EditorMode.SELECT)
    assert button.bgcolor == ft.Colors.WHITE


@patch('edit_events._set_mode_button_state')
def test_refresh_mode_buttons(mock_set_state, mock_app):
    mock_app.attr.editor_mode = EditorMode.TRANSITIONS
    edit_events.refresh_mode_buttons(mock_app)
    assert mock_set_state.call_count == 3


@patch('edit_events.refresh_mode_buttons')
def test_set_editor_mode(mock_refresh, mock_app):
    edit_events.set_editor_mode(mock_app, EditorMode.NODES)
    assert mock_app.attr.editor_mode == EditorMode.NODES
    mock_refresh.assert_called_once_with(mock_app)
    mock_app.page.update.assert_called_once()


def test_scale_graph_positions(mock_app):
    node = MagicMock(x=400, y=300)
    mock_app.graph.nodes = {node}
    edit_events._scale_graph_positions(mock_app, 1.0, 2.0)
    assert node.x == 400
    assert node.y == 300

    node2 = MagicMock(x=600, y=300)
    mock_app.graph.nodes = {node2}
    edit_events._scale_graph_positions(mock_app, 1.0, 2.0)
    assert node2.x == 800
    assert node2.y == 300


def test_clamp_canvas_scale(mock_app):
    assert edit_events._clamp_canvas_scale(3.0, mock_app) == 2.0
    assert edit_events._clamp_canvas_scale(0.1, mock_app) == 0.5
    assert edit_events._clamp_canvas_scale(1.5, mock_app) == 1.5


def test_sync_canvas_size(mock_app):
    edit_events._sync_canvas_size(mock_app)
    assert mock_app.ui.drawing_area.width == 800
    assert mock_app.ui.canvas_container.height == 600
    assert mock_app.ui.canvas_scale_slider.value == 100
    assert mock_app.ui.canvas_scale_text.value == "100%"


@patch('edit_events.draw_nodes')
@patch('edit_events._sync_canvas_size')
def test_set_canvas_scale(mock_sync, mock_draw, mock_app):
    edit_events.set_canvas_scale(1.5, mock_app)
    assert mock_app.attr.canvas_scale == 1.5
    assert mock_app.attr.canvas_width == 1200
    mock_sync.assert_called_once_with(mock_app)
    mock_draw.assert_called_once_with(mock_app)
    mock_app.page.update.assert_called_once()


@patch('edit_events.set_canvas_scale')
def test_set_canvas_scale_from_slider(mock_set_scale, mock_app):
    e = MagicMock()
    e.control.value = 150
    edit_events.set_canvas_scale_from_slider(e, mock_app)
    mock_set_scale.assert_called_once_with(1.5, mock_app)


@patch('edit_events.set_canvas_scale')
def test_zoom_canvas_in(mock_set_scale, mock_app):
    edit_events.zoom_canvas_in(mock_app)
    mock_set_scale.assert_called_once_with(1.1, mock_app)


@patch('edit_events.set_canvas_scale')
def test_zoom_canvas_out(mock_set_scale, mock_app):
    edit_events.zoom_canvas_out(mock_app)
    mock_set_scale.assert_called_once_with(0.9, mock_app)


@patch('edit_events.set_editor_mode')
def test_activation_helpers(mock_set_mode, mock_app):
    edit_events.activate_selection_mode(mock_app)
    mock_set_mode.assert_called_with(mock_app, EditorMode.SELECT)

    edit_events.activate_node_creation_mode(mock_app)
    mock_set_mode.assert_called_with(mock_app, EditorMode.NODES)

    edit_events.activate_transition_creation_mode(mock_app)
    mock_set_mode.assert_called_with(mock_app, EditorMode.TRANSITIONS)

    edit_events.toggle_placing_mode(mock_app)
    mock_set_mode.assert_called_with(mock_app, EditorMode.NODES)

    edit_events.toggle_transition_mode(mock_app)
    mock_set_mode.assert_called_with(mock_app, EditorMode.TRANSITIONS)


@patch('edit_events.draw_nodes')
def test_toggle_start_state(mock_draw, mock_app):
    node = MagicMock()
    node.type = NodeType.NORMAL
    mock_app.graph.selected_node = node
    
    edit_events.toggle_start_state(mock_app)
    
    assert node.type == NodeType.START
    mock_draw.assert_called_once()


@patch('edit_events.draw_nodes')
def test_toggle_final_state(mock_draw, mock_app):
    node = MagicMock()
    node.type = NodeType.NORMAL
    mock_app.graph.selected_node = node

    edit_events.toggle_final_state(mock_app)
    
    assert node.type == NodeType.FINAL
    mock_draw.assert_called_once()


def test_add_alphabet_symbols(mock_app):
    mock_app.ui.alphabet_input.value = "a, b, c "
    edit_events.add_alphabet_symbols(mock_app)
    assert mock_app.attr.alphabet == {'a', 'b', 'c'}
    assert mock_app.ui.alphabet_input.value == ""
    mock_app.page.update.assert_called_once()


def test_remove_alphabet_symbols(mock_app):
    mock_app.attr.alphabet = {'a', 'b', 'c'}
    mock_app.ui.alphabet_input.value = "a, c"
    edit_events.remove_alphabet_symbols(mock_app)
    assert mock_app.attr.alphabet == {'b'}
    assert mock_app.ui.alphabet_input.value == ""
    mock_app.page.update.assert_called_once()


@patch('edit_events.draw_nodes')
@patch('edit_events._sync_canvas_size')
@patch('edit_events.refresh_mode_buttons')
def test_clear_automaton(mock_refresh, mock_sync, mock_draw, mock_app):
    edit_events.clear_automaton(mock_app)
    mock_app.history.add.assert_called_once()
    assert isinstance(mock_app.graph, Graph)
    assert isinstance(mock_app.attr, ApplicationState)
    mock_sync.assert_called_once()
    mock_refresh.assert_called_once()
    mock_draw.assert_called_once()


@patch('edit_events.draw_nodes')
def test_handle_delete_node(mock_draw, mock_app):
    node1 = MagicMock()
    node2 = MagicMock()
    transition = MagicMock()
    transition.start = node1
    transition.end = node2
    
    mock_app.graph.nodes = {node1, node2}
    mock_app.graph.transitions = {transition}
    mock_app.graph.selected_node = node1
    
    edit_events.handle_delete(mock_app)
    
    assert node1 not in mock_app.graph.nodes
    assert node2 in mock_app.graph.nodes
    assert transition not in mock_app.graph.transitions
    assert mock_app.graph.selected_node is None
    mock_app.history.add.assert_called_once()
    mock_draw.assert_called_once()


@patch('edit_events.draw_nodes')
def test_handle_delete_transition(mock_draw, mock_app):
    transition = MagicMock()
    mock_app.graph.transitions = {transition}
    mock_app.graph.selected_transition = transition
    
    edit_events.handle_delete(mock_app)
    
    assert transition not in mock_app.graph.transitions
    assert mock_app.graph.selected_transition is None
    mock_app.history.add.assert_called_once()
    mock_draw.assert_called_once()