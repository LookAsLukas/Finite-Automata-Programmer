import math
from flet import (
    Text,
    TextField,
    ElevatedButton,
    AlertDialog
)
from draw import draw_nodes


def add_node(e, attr, ui):
    if not attr.placing_mode:
        return
    x, y = e.local_x, e.local_y
    new_name = f"q{attr.node_counter}"
    attr.nodes[new_name] = (x, y)
    attr.node_counter += 1
    draw_nodes(attr, ui)


def get_clicked_node(x, y, attr):
    for name, (nx, ny) in attr.nodes.items():
        if (x - nx) ** 2 + (y - ny) ** 2 <= 30 ** 2:
            return name
    return None


def rename_state(name, attr, ui, page):
    def on_submit(e):
        new_name = input_field.value.strip()
        if not new_name or new_name in attr.nodes:
            ui.status_text.value = "Некорректное или занятое имя!"
            page.close(dialog)
            page.update()
            return

        attr.nodes[new_name] = attr.nodes.pop(name)

        new_transitions = {}
        for s, lst in attr.transitions.items():
            updated_s = new_name if s == name else s
            updated_list = []
            for t in lst:
                t_copy = t.copy()
                if t_copy["end"] == name:
                    t_copy["end"] = new_name
                updated_list.append(t_copy)
            new_transitions[updated_s] = updated_list
        attr.transitions.clear()
        attr.transitions.update(new_transitions)

        if attr.start_state == name:
            attr.start_state = new_name
        if name in attr.final_states:
            attr.final_states.remove(name)
            attr.final_states.add(new_name)
        if attr.selected_node == name:
            attr.selected_node = new_name

        ui.status_text.value = f"Состояние {name} переименовано в {new_name}"
        page.close(dialog)
        draw_nodes(attr, ui)
        page.update()

    input_field = TextField(label="Новое имя состояния", value=name, autofocus=True)
    dialog = AlertDialog(
        modal=True,
        title=Text("Переименование состояния"),
        content=input_field,
        actions=[
            ElevatedButton("OK", on_click=on_submit),
            ElevatedButton("Отмена", on_click=lambda e: page.close(dialog)),
        ],
    )

    page.open(dialog) 


def handle_canvas_click(e, attr, ui, page):
    x, y = e.local_x, e.local_y
    clicked = get_clicked_node(x, y, attr)

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


def get_clicked_transition(x, y, attr):
    threshold = 10  
    for start, trans_list in attr.transitions.items():
        if start not in attr.nodes:
            continue
        (x1, y1) = attr.nodes[start]
        for t in trans_list:
            end = t["end"]
            if end not in attr.nodes:
                continue
            (x2, y2) = attr.nodes[end]

            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx ** 2 + dy ** 2)
            if length == 0:
                continue

            ux, uy = dx / length, dy / length
            start_x, start_y = x1 + ux * 30, y1 + uy * 30
            end_x, end_y = x2 - ux * 30, y2 - uy * 30

            px, py = x, y
            line_dist = abs((end_y - start_y) * px - (end_x - start_x) * py + end_x * start_y - end_y * start_x) / length
            if line_dist <= threshold:
                dot = ((px - start_x) * (end_x - start_x) + (py - start_y) * (end_y - start_y)) / (length ** 2)
                if 0 <= dot <= 1:
                    return start, t
    return None, None


def edit_transition_symbol(start, transition, attr, ui, page):
    def on_submit(e):
        new_symbol = input_field.value.strip()
        if not new_symbol:
            ui.status_text.value = "Символ не может быть пустым!"
            page.close(dialog)
            page.update()
            return

        transition["symbol"] = new_symbol
        ui.status_text.value = f"Переход {start} → {transition['end']} изменён на '{new_symbol}'"
        page.close(dialog)
        draw_nodes(attr, ui)
        page.update()

    input_field = TextField(label="Новый символ перехода", value=transition["symbol"], autofocus=True)
    dialog = AlertDialog(
        modal=True,
        title=Text("Редактирование символа перехода"),
        content=input_field,
        actions=[
            ElevatedButton("OK", on_click=on_submit),
            ElevatedButton("Отмена", on_click=lambda e: page.close(dialog)),
        ],
    )
    page.open(dialog)


def handle_double_click(e, attr, ui, page):
    if attr.placing_mode or attr.transition_mode:
        return
    x, y = e.local_x, e.local_y

    clicked_node = get_clicked_node(x, y, attr)
    if clicked_node:
        rename_state(clicked_node, attr, ui, page)
        return

    start, transition = get_clicked_transition(x, y, attr)
    if transition:
        edit_transition_symbol(start, transition, attr, ui, page)
