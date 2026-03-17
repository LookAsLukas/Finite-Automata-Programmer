from __future__ import annotations

from draw import draw_nodes
from graph import NodeType, Graph
from application_state import ApplicationState, ApplicationUI


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

    app.ui.canvas_scale_text.value = f"Размер поля: {int(round(app.attr.canvas_scale * 100))}%"


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


def toggle_placing_mode(app: Application):
    app.attr.placing_mode = not app.attr.placing_mode
    if app.attr.placing_mode:
        app.attr.transition_mode = False
    app.ui.mode_status.value = "Mode: Nodes" if app.attr.placing_mode else "Mode: Normal"
    app.page.update()


def toggle_transition_mode(app: Application):
    app.attr.transition_mode = not app.attr.transition_mode
    if app.attr.transition_mode:
        app.attr.placing_mode = False
    app.ui.mode_status.value = "Mode: Transitions" if app.attr.transition_mode else "Mode: Normal"
    app.page.update()


def toggle_start_state(app: Application):
    if app.attr.transition_mode or app.attr.placing_mode:
        return
    if app.graph.selected_node is None:
        app.ui.status_text.value = "Выберите узел!"
        app.page.update()
        return

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
    if app.attr.transition_mode or app.attr.placing_mode:
        return
    if app.graph.selected_node is None:
        app.ui.status_text.value = "Выберите узел!"
        app.page.update()
        return

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


def clear_automaton(app: Application):
    app.graph = Graph()
    app.attr = ApplicationState()
    app.ui = ApplicationUI()
    draw_nodes(app)
    app.page.update()


def handle_delete(app: Application):
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
