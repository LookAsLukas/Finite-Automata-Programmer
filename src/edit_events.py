from __future__ import annotations

import flet as ft

from draw import draw_nodes
from graph import NodeType, Graph
from application_state import ApplicationState, EditorMode

_MODE_BUTTON_ACCENTS = {
    EditorMode.SELECT: {
        "bgcolor": "#dbeafe",
        "color": "#1d4ed8",
        "border": "#60a5fa",
    },
    EditorMode.NODES: {
        "bgcolor": "#ffedd5",
        "color": "#c2410c",
        "border": "#fb923c",
    },
    EditorMode.TRANSITIONS: {
        "bgcolor": "#dcfce7",
        "color": "#15803d",
        "border": "#4ade80",
    },
}
_MODE_BUTTON_INACTIVE = {
    "bgcolor": ft.Colors.WHITE,
    "color": ft.Colors.BLUE_GREY_700,
    "border": ft.Colors.BLUE_GREY_100,
}


def _build_mode_button_style(border_color: str, active: bool) -> ft.ButtonStyle:
    return ft.ButtonStyle(
        padding=ft.padding.symmetric(horizontal=16, vertical=16),
        shape=ft.RoundedRectangleBorder(radius=14),
        side={ft.ControlState.DEFAULT: ft.BorderSide(1.5, border_color)},
        elevation={ft.ControlState.DEFAULT: 1 if active else 0},
        animation_duration=180,
    )


def _set_mode_button_state(button, mode: EditorMode, active_mode: EditorMode) -> None:
    if button is None:
        return

    colors = _MODE_BUTTON_ACCENTS[mode] if mode is active_mode else _MODE_BUTTON_INACTIVE
    is_active = mode is active_mode

    button.bgcolor = colors["bgcolor"]
    button.color = colors["color"]
    button.icon_color = colors["color"]
    button.style = _build_mode_button_style(colors["border"], is_active)


def refresh_mode_buttons(app: Application) -> None:
    active_mode = app.attr.editor_mode
    _set_mode_button_state(app.ui.mode_select_button, EditorMode.SELECT, active_mode)
    _set_mode_button_state(app.ui.mode_nodes_button, EditorMode.NODES, active_mode)
    _set_mode_button_state(app.ui.mode_transitions_button, EditorMode.TRANSITIONS, active_mode)


def set_editor_mode(app: Application, mode: EditorMode, update_page: bool = True) -> None:
    app.attr.editor_mode = mode
    refresh_mode_buttons(app)

    if update_page:
        app.page.update()


def _scale_graph_positions(app: Application, old_scale: float, new_scale: float) -> None:
    if not app.graph.nodes:
        return

    scale_ratio = new_scale / old_scale
    if scale_ratio == 1.0:
        return

    old_center_x = app.attr.canvas_width / 2
    old_center_y = app.attr.canvas_height / 2
    new_canvas_width = app.attr.base_canvas_width * new_scale
    new_canvas_height = app.attr.base_canvas_height * new_scale

    for node in app.graph.nodes:
        node.x = old_center_x + (node.x - old_center_x) * scale_ratio
        node.y = old_center_y + (node.y - old_center_y) * scale_ratio

    min_x = min(node.x for node in app.graph.nodes)
    max_x = max(node.x for node in app.graph.nodes)
    min_y = min(node.y for node in app.graph.nodes)
    max_y = max(node.y for node in app.graph.nodes)

    shift_x = 0
    if min_x < app.config.node_radius:
        shift_x = app.config.node_radius - min_x
    elif max_x > new_canvas_width - app.config.node_radius:
        shift_x = (new_canvas_width - app.config.node_radius) - max_x

    shift_y = 0
    if min_y < app.config.node_radius:
        shift_y = app.config.node_radius - min_y
    elif max_y > new_canvas_height - app.config.node_radius:
        shift_y = (new_canvas_height - app.config.node_radius) - max_y

    if shift_x != 0 or shift_y != 0:
        for node in app.graph.nodes:
            node.x += shift_x
            node.y += shift_y


def _clamp_canvas_scale(scale: float, app: Application) -> float:
    return max(app.attr.min_canvas_scale, min(app.attr.max_canvas_scale, scale))


def _sync_canvas_size(app: Application) -> None:
    app.ui.drawing_area.width = app.attr.canvas_width
    app.ui.drawing_area.height = app.attr.canvas_height

    if app.ui.canvas_container is not None:
        app.ui.canvas_container.width = app.attr.canvas_width
        app.ui.canvas_container.height = app.attr.canvas_height

    if app.ui.canvas_scale_slider is not None:
        app.ui.canvas_scale_slider.value = app.attr.canvas_scale * 100

    app.ui.canvas_scale_text.value = f"{int(round(app.attr.canvas_scale * 100))}%"


def set_canvas_scale(scale: float, app: Application) -> None:
    new_canvas_scale = _clamp_canvas_scale(scale, app)
    if new_canvas_scale != app.attr.canvas_scale:
        _scale_graph_positions(app, app.attr.canvas_scale, new_canvas_scale)

    app.attr.canvas_scale = new_canvas_scale
    app.attr.canvas_width = app.attr.base_canvas_width * app.attr.canvas_scale
    app.attr.canvas_height = app.attr.base_canvas_height * app.attr.canvas_scale
    _sync_canvas_size(app)
    draw_nodes(app)
    app.page.update()


def set_canvas_scale_from_slider(e, app: Application) -> None:
    set_canvas_scale(e.control.value / 100, app)


def zoom_canvas_in(app: Application) -> None:
    set_canvas_scale(app.attr.canvas_scale + app.attr.canvas_scale_step, app)


def zoom_canvas_out(app: Application) -> None:
    set_canvas_scale(app.attr.canvas_scale - app.attr.canvas_scale_step, app)


def activate_selection_mode(app: Application) -> None:
    set_editor_mode(app, EditorMode.SELECT)


def activate_node_creation_mode(app: Application) -> None:
    set_editor_mode(app, EditorMode.NODES)


def activate_transition_creation_mode(app: Application) -> None:
    set_editor_mode(app, EditorMode.TRANSITIONS)


def toggle_placing_mode(app: Application):
    activate_node_creation_mode(app)


def toggle_transition_mode(app: Application):
    activate_transition_creation_mode(app)


def toggle_start_state(app: Application):
    if app.graph.selected_node is None:
        app.ui.status_text.value = "Выберите узел!"
        app.page.update()
        return

    app.history.add(app.graph)

    if app.graph.selected_node in app.graph.get_start_states():
        if app.graph.selected_node.type == NodeType.START:
            app.graph.selected_node.type = NodeType.NORMAL
        elif app.graph.selected_node.type == NodeType.START_FINAL:
            app.graph.selected_node.type = NodeType.FINAL
    else:
        if app.graph.selected_node.type == NodeType.NORMAL:
            app.graph.selected_node.type = NodeType.START
        elif app.graph.selected_node.type == NodeType.FINAL:
            app.graph.selected_node.type = NodeType.START_FINAL

    draw_nodes(app)
    app.page.update()


def toggle_final_state(app: Application):
    if app.graph.selected_node is None:
        app.ui.status_text.value = "Выберите узел!"
        app.page.update()
        return

    app.history.add(app.graph)

    if app.graph.selected_node in app.graph.get_final_states():
        if app.graph.selected_node.type == NodeType.FINAL:
            app.graph.selected_node.type = NodeType.NORMAL
        elif app.graph.selected_node.type == NodeType.START_FINAL:
            app.graph.selected_node.type = NodeType.START
    else:
        if app.graph.selected_node.type == NodeType.NORMAL:
            app.graph.selected_node.type = NodeType.FINAL
        elif app.graph.selected_node.type == NodeType.START:
            app.graph.selected_node.type = NodeType.START_FINAL

    draw_nodes(app)
    app.page.update()


def add_alphabet_symbols(app: Application):
    symbols = set(app.ui.alphabet_input.value.strip().replace(' ', '').replace(',', ''))
    if symbols != set():
        app.attr.alphabet.update(symbols)
        app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"
        app.ui.alphabet_input.value = ""
        app.ui.status_text.value = f"Добавлены символы '{''.join(symbols)}'"
    else:
        app.ui.status_text.value = "Введите хотя бы один символ!"
    app.page.update()


def remove_alphabet_symbols(app: Application):
    symbols = set(app.ui.alphabet_input.value.strip().replace(' ', '').replace(',', ''))
    if symbols != set():
        app.attr.alphabet.difference_update(symbols)
        app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"
        app.ui.alphabet_input.value = ""
        app.ui.status_text.value = f"Удалены символы '{''.join(symbols)}'"
    else:
        app.ui.status_text.value = "Введите хотя бы один символ!"
    app.page.update()


def clear_automaton(app: Application):
    app.history.add(app.graph)

    app.graph = Graph()
    app.attr = ApplicationState()
    _sync_canvas_size(app)
    refresh_mode_buttons(app)
    app.ui.alphabet_display.value = "Алфавит: ∅"
    app.ui.status_text.value = "Готов к работе"
    app.ui.regex_display.value = "Регулярное выражение: не задано"
    draw_nodes(app)
    app.page.update()


def handle_delete(app: Application):
    if app.graph.selected_node or app.graph.selected_transition:
        app.history.add(app.graph)

    if app.graph.selected_node is not None:
        app.graph.nodes.remove(app.graph.selected_node)
        app.graph.transitions = {
            transition
            for transition in app.graph.transitions
            if transition.start != app.graph.selected_node and
            transition.end != app.graph.selected_node
        }
    elif app.graph.selected_transition:
        app.graph.transitions.remove(app.graph.selected_transition)
    else:
        app.ui.status_text.value = "Ничего не выбрано для удаления"

    app.graph.selected_node = None
    app.graph.selected_transition = None

    draw_nodes(app)
    app.page.update()
