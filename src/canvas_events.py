from canvas_utils import get_clicked_node, get_clicked_transition
from dialog_handlers import rename_state_dialog, edit_transition_dialog
from fap import Application
from graph import Node, Transition
from linal import Vector2D


def _event_point(e) -> Vector2D:
    return Vector2D(e.local_x, e.local_y)


def _is_inside_canvas(point: Vector2D, app: Application) -> bool:
    return 0 <= point.x <= app.attr.canvas_width and 0 <= point.y <= app.attr.canvas_height


def add_node(click: Vector2D, app: Application) -> None:
    """Добавляет узел в позиции клика"""
    if not app.attr.placing_mode:
        return

    # Проверяем, что клик внутри канваса (с учетом границ для узла)
    if click.x < app.config.node_radius or click.x > app.attr.canvas_width - app.config.node_radius or \
       click.y < app.config.node_radius or click.y > app.attr.canvas_height - app.config.node_radius:
        return  # Клик слишком близко к краю

    app.history.add(app.graph)

    name = f"q{app.graph.node_counter}"
    node = Node(
        x=click.x, y=click.y,
        name=name)
    app.graph.nodes.add(node)
    app.graph.node_counter += 1
    app.draw.update_node(node)


def handle_canvas_click(e, app: Application) -> None:
    """Обрабатывает одиночный клик на canvas"""
    click = _event_point(e)

    # Проверяем, что клик внутри области канваса
    if not _is_inside_canvas(click, app):
        return  # Клик вне канваса

    clicked_node = get_clicked_node(click, app)
    clicked_transition = get_clicked_transition(click, app)

    if app.attr.placing_mode:
        add_node(click, app)
        return

    if clicked_node is not None:
        if app.graph.selected_node is not None and app.attr.transition_mode:
            app.history.add(app.graph)

            if app.attr.alphabet == set():
                app.attr.alphabet.add("a")
            symbol = next(iter(app.attr.alphabet))
            transition = Transition(
                start=app.graph.selected_node,
                end=clicked_node,
                symbols=symbol)

            if len(list(filter(lambda tr: tr.start == transition.start and tr.end == transition.end,
                               app.graph.transitions))) == 0:
                app.graph.transitions.add(transition)
                app.draw.update_transition(transition)

        prev_selected = app.graph.selected_node
        app.graph.selected_node = clicked_node
        app.draw.update_node(prev_selected)
        app.draw.update_node(app.graph.selected_node)

        prev_selected = app.graph.selected_transition
        app.graph.selected_transition = None
        app.draw.update_transition(prev_selected)
    elif clicked_transition is not None:
        prev_selected = app.graph.selected_transition
        app.graph.selected_transition = clicked_transition
        app.draw.update_transition(prev_selected)
        app.draw.update_transition(app.graph.selected_transition)

        prev_selected = app.graph.selected_node
        app.graph.selected_node = None
        app.draw.update_node(prev_selected)
    else:
        prev_selected = app.graph.selected_node
        app.graph.selected_node = None
        app.draw.update_node(prev_selected)

        prev_selected = app.graph.selected_transition
        app.graph.selected_transition = None
        app.draw.update_transition(prev_selected)

    app.page.update()


def handle_double_click(e, app: Application) -> None:
    """Обрабатывает двойной клик на canvas"""
    if app.attr.placing_mode or app.attr.transition_mode:
        return

    click = _event_point(e)

    if not _is_inside_canvas(click, app):
        return

    clicked_node = get_clicked_node(click, app)
    if clicked_node is not None:
        dialog = rename_state_dialog(clicked_node, app)
        app.page.open(dialog)
        return

    clicked_transition = get_clicked_transition(click, app)
    if clicked_transition is not None:
        dialog = edit_transition_dialog(clicked_transition, app)
        app.page.open(dialog)


def handle_drag_start(e, app: Application) -> None:
    """Начало перетаскивания узла"""
    if app.attr.placing_mode or app.attr.transition_mode:
        return

    click = _event_point(e)

    if not _is_inside_canvas(click, app):
        return

    clicked_node = get_clicked_node(click, app)

    if clicked_node:
        app.history.add(app.graph)

        app.graph.dragging_node = clicked_node
        app.draw.update_node(clicked_node)
        app.page.update()


def handle_drag_update(e, app: Application) -> None:
    """Обновление позиции перетаскиваемого узла"""
    if app.graph.dragging_node:
        click = _event_point(e)

        x = max(app.config.node_radius, min(app.attr.canvas_width - app.config.node_radius, click.x))
        y = max(app.config.node_radius, min(app.attr.canvas_height - app.config.node_radius, click.y))

        app.graph.dragging_node.x = x
        app.graph.dragging_node.y = y
        app.draw.update_node(app.graph.dragging_node)
        app.page.update()


def handle_drag_end(e, app: Application):
    """Завершение перетаскивания"""
    if app.graph.dragging_node:
        app.graph.dragging_node = None
        app.page.update()
