from draw import draw_nodes
from fap import Application
from graph import NodeType, Graph
from application_state import ApplicationState, ApplicationUI


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
    app.attr.canvas_scale = _clamp_canvas_scale(scale, app)
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
