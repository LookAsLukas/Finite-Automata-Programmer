from draw import draw_nodes


def toggle_placing_mode(e, attr, ui, page):
    attr.placing_mode = not attr.placing_mode
    if attr.placing_mode:
        attr.transition_mode = False
        attr.first_selected_node = None
    ui.mode_status.value = "Режим размещения: ВКЛЮЧЕН" if attr.placing_mode else "Режим размещения: выключен"
    page.update()


def toggle_transition_mode(e, attr, ui, page):
    attr.transition_mode = not attr.transition_mode
    if attr.transition_mode:
        attr.placing_mode = False
        attr.first_selected_node = None
    ui.transition_status.value = "Режим переходов: ВКЛЮЧЕН" if attr.transition_mode else "Режим переходов: выключен"
    page.update()


def toggle_start_state(e, attr, ui, page):
    if attr.transition_mode or attr.placing_mode:
        return
    if attr.selected_node is None:
        ui.status_text.value = "Выберите узел!"
        page.update()
        return
    if attr.start_state == attr.selected_node:
        attr.start_state = None
        ui.status_text.value = f"{attr.selected_node} больше не начальное состояние"
    else:
        attr.start_state = attr.selected_node
        ui.status_text.value = f"{attr.selected_node} теперь начальное состояние"
    draw_nodes(attr, ui)
    page.update()


def toggle_final_state(e, attr, ui, page):
    if attr.transition_mode or attr.placing_mode:
        return
    if attr.selected_node is None:
        ui.status_text.value = "Выберите узел!"
        page.update()
        return
    if attr.selected_node in attr.final_states:
        attr.final_states.remove(attr.selected_node)
        ui.status_text.value = f"{attr.selected_node} больше не конечное состояние"
    else:
        attr.final_states.add(attr.selected_node)
        ui.status_text.value = f"{attr.selected_node} теперь конечное состояние"
    draw_nodes(attr, ui)
    page.update()


def add_alphabet_symbol(e, attr, ui, page):
    symbol = ui.alphabet_input.value.strip()
    if symbol and len(symbol) == 1:
        attr.alphabet.add(symbol)
        ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(attr.alphabet))}"
        ui.alphabet_input.value = ""
        ui.status_text.value = f"Добавлен символ '{symbol}'"
    else:
        ui.status_text.value = "Введите один символ!"
    page.update()


def clear_automaton(e, attr, ui, page):
    attr.nodes.clear()
    attr.node_counter = 0
    attr.start_state = None
    attr.final_states.clear()
    attr.transitions.clear()
    attr.selected_node = None
    attr.first_selected_node = None
    attr.placing_mode = False
    attr.transition_mode = False
    attr.alphabet.clear()

    ui.drawing_area.shapes = []
    ui.mode_status.value = "Режим размещения: выключен"
    ui.transition_status.value = "Режим рисования переходов: выключен"
    ui.status_text.value = "Автомат очищен"
    ui.alphabet_display.value = "Алфавит: ∅"
    ui.alphabet_input.value = ""
    page.update()
