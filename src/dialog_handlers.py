from flet import Text, TextField, ElevatedButton, AlertDialog

def rename_state_dialog(name: str, attr, ui, page):
    """Создает диалог для переименования состояния."""
    def on_submit(e):
        new_name = input_field.value.strip()
        if not new_name or new_name in attr.nodes:
            ui.status_text.value = "Некорректное или занятое имя!"
            page.close(dialog)
            page.update()
            return

        # Обновляем данные
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
        # Импортируем здесь чтобы избежать циклического импорта
        from draw import draw_nodes
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
    return dialog


def edit_transition_dialog(start: str, transition: dict, attr, ui, page):
    """Создает диалог для редактирования символа перехода."""
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
        from draw import draw_nodes
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
    return dialog

def regex_input_dialog(attr, ui, page):
    def on_submit(e):
        regex_str = input_field.value.strip()
        if not regex_str:
            ui.status_text.value = "Введите регулярное выражение!"
            page.close(dialog)
            page.update()
            return

        page.close(dialog)
        
        from automata_operations import convert_regex_to_nfa, import_automaton_data
        from draw import draw_nodes
        
        # Пробуем преобразовать regex в NFA
        nfa = convert_regex_to_nfa(regex_str)
        
        if nfa is None:
            error_dialog = AlertDialog(
                modal=True,
                title=Text("Ошибка синтаксиса"),
                content=Text(f"Регулярное выражение '{regex_str}' содержит синтаксические ошибки."),
                actions=[
                    ElevatedButton("OK", on_click=lambda e: page.close(error_dialog)),
                ],
            )
            page.open(error_dialog)
            ui.status_text.value = f"❌ Ошибка в регулярном выражении: '{regex_str}'"
        else:
            # Сохраняем регулярное выражение
            attr.regex = regex_str
            ui.regex_display.value = f"Регулярное выражение: {regex_str}"
            
            # Импортируем автомат
            if import_automaton_data(nfa, attr, ui):
                draw_nodes(attr, ui)
                ui.status_text.value = f"✅ Автомат построен из регулярного выражения: {regex_str}"
            else:
                ui.status_text.value = f"❌ Ошибка при построении автомата из регулярного выражения"
        
        page.update()

    input_field = TextField(
        label="Регулярное выражение", 
        hint_text="Пример: (a|b)*abb",
        autofocus=True,
        width=400
    )
    dialog = AlertDialog(
        modal=True,
        title=Text("Построение автомата из регулярного выражения"),
        content=input_field,
        actions=[
            ElevatedButton("Построить", on_click=on_submit),
            ElevatedButton("Отмена", on_click=lambda e: page.close(dialog)),
        ],
    )
    return dialog