from canvas_utils import get_clicked_node, get_clicked_transition
from dialog_handlers import rename_state_dialog, edit_transition_dialog
from draw import draw_nodes


def add_node(e, attr, ui):
    """Добавляет узел в позиции клика"""
    if not attr.placing_mode:
        return
    x, y = e.local_x, e.local_y
    new_name = f"q{attr.node_counter}"
    attr.nodes[new_name] = (x, y)
    attr.node_counter += 1
    draw_nodes(attr, ui)


def handle_canvas_click(e, attr, ui, page):
    """Обрабатывает одиночный клик на canvas"""
    x, y = e.local_x, e.local_y
    clicked = get_clicked_node(x, y, attr.nodes)

    if attr.placing_mode:
        add_node(e, attr, ui)
        return

    if attr.transition_mode and clicked is not None:
        if attr.first_selected_node is None:
            attr.first_selected_node = clicked
            ui.transition_status.value = f"Выбрано начальное состояние: {clicked}"
        else:
            start = attr.first_selected_node
            end = clicked
            symbol = next(iter(attr.alphabet)) if attr.alphabet else "a"
            attr.transitions.setdefault(start, []).append({"symbol": symbol, "end": end})
            attr.first_selected_node = None
            ui.transition_status.value = f"Переход {start} → {end} добавлен"
        draw_nodes(attr, ui)
        page.update()
        return

    if not attr.placing_mode and not attr.transition_mode:
        if clicked is not None:
            attr.selected_node = clicked
            ui.status_text.value = f"Выбран узел: {clicked}"
            draw_nodes(attr, ui)
            page.update()


def handle_double_click(e, attr, ui, page):
    """Обрабатывает двойной клик на canvas"""
    if attr.placing_mode or attr.transition_mode:
        return
    x, y = e.local_x, e.local_y

    clicked_node = get_clicked_node(x, y, attr.nodes)
    if clicked_node:
        dialog = rename_state_dialog(clicked_node, attr, ui, page)
        page.open(dialog)
        return

    start, transition = get_clicked_transition(x, y, attr.nodes, attr.transitions)
    if transition:
        dialog = edit_transition_dialog(start, transition, attr, ui, page)
        page.open(dialog)