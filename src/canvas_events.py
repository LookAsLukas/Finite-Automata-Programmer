from canvas_utils import get_clicked_node, get_clicked_transition
from dialog_handlers import rename_state_dialog, edit_transition_dialog
from draw import draw_nodes


def add_node(e, attr, ui):
    """Добавляет узел в позиции клика"""
    if not attr.placing_mode:
        return
    
    # Получаем координаты клика относительно контейнера
    x, y = e.local_x, e.local_y
    
    # Проверяем, что клик внутри канваса (с учетом границ для узла)
    if x < 30 or x > attr.canvas_width - 30 or y < 30 or y > attr.canvas_height - 30:
        return  # Клик слишком близко к краю
    
    new_name = f"q{attr.node_counter}"
    attr.nodes[new_name] = (x, y)
    attr.node_counter += 1
    draw_nodes(attr, ui)


def handle_canvas_click(e, attr, ui, page):
    """Обрабатывает одиночный клик на canvas"""
    x, y = e.local_x, e.local_y
    
    # Проверяем, что клик внутри области канваса
    if x < 0 or x > attr.canvas_width or y < 0 or y > attr.canvas_height:
        return  # Клик вне канваса
    
    clicked_node = get_clicked_node(x, y, attr.nodes)
    clicked_start, clicked_transition = get_clicked_transition(x, y, attr.nodes, attr.transitions)

    if hasattr(attr, 'selected_transition'):
        attr.selected_transition = None

    if attr.placing_mode:
        add_node(e, attr, ui)
        return

    if attr.transition_mode and clicked_node is not None:
        if attr.first_selected_node is None:
            attr.first_selected_node = clicked_node
            ui.transition_status.value = f"Выбрано начальное состояние: {clicked_node}"
        else:
            start = attr.first_selected_node
            end = clicked_node
            symbol = next(iter(attr.alphabet)) if attr.alphabet else "a"
            attr.transitions.setdefault(start, []).append({"symbol": symbol, "end": end})
            attr.first_selected_node = None
            ui.transition_status.value = f"Переход {start} → {end} добавлен"
        draw_nodes(attr, ui)
        page.update()
        return

    if not attr.placing_mode and not attr.transition_mode:
        if clicked_transition:
            attr.selected_transition = (clicked_start, clicked_transition)
            attr.selected_node = None
            symbol = clicked_transition["symbol"]
            end = clicked_transition["end"]
            ui.status_text.value = f"Выбран переход: {clicked_start} → {end} ('{symbol}')"
        elif clicked_node is not None:
            attr.selected_node = clicked_node
            ui.status_text.value = f"Выбран узел: {clicked_node}"
        else:
            attr.selected_node = None
            ui.status_text.value = "Сброс выбора"
        
        draw_nodes(attr, ui)
        page.update()

def handle_double_click(e, attr, ui, page):
    """Обрабатывает двойной клик на canvas"""
    if attr.placing_mode or attr.transition_mode:
        return
    
    x, y = e.local_x, e.local_y
    
    if x < 0 or x > attr.canvas_width or y < 0 or y > attr.canvas_height:
        return 
    
    clicked_node = get_clicked_node(x, y, attr.nodes)
    if clicked_node:
        dialog = rename_state_dialog(clicked_node, attr, ui, page)
        page.open(dialog)
        return

    start, transition = get_clicked_transition(x, y, attr.nodes, attr.transitions)
    if transition:
        dialog = edit_transition_dialog(start, transition, attr, ui, page)
        page.open(dialog)


def handle_drag_start(e, attr, ui, page):
    """Начало перетаскивания узла"""
    if attr.placing_mode or attr.transition_mode:
        return
    
    x, y = e.local_x, e.local_y
    
    if x < 0 or x > attr.canvas_width or y < 0 or y > attr.canvas_height:
        return 
    
    clicked_node = get_clicked_node(x, y, attr.nodes)
    
    if clicked_node:
        attr.dragging_node = clicked_node
        attr.selected_node = clicked_node
        ui.status_text.value = f"Перетаскивание состояния {clicked_node}"
        draw_nodes(attr, ui)
        page.update()

def handle_drag_update(e, attr, ui, page):
    """Обновление позиции перетаскиваемого узла"""
    if attr.dragging_node:
        x, y = e.local_x, e.local_y
        
        x = max(30, min(attr.canvas_width - 30, x))
        y = max(30, min(attr.canvas_height - 30, y))
        
        attr.nodes[attr.dragging_node] = (x, y)
        draw_nodes(attr, ui)
        page.update()

def handle_drag_end(e, attr, ui, page):
    """Завершение перетаскивания"""
    if attr.dragging_node:
        ui.status_text.value = f"Состояние {attr.dragging_node} перемещено"
        attr.dragging_node = None
        page.update()