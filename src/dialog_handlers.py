from flet import Text, TextField, ElevatedButton, AlertDialog, Row, MainAxisAlignment
from application_state import EPSILON_SYMBOL

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

        from draw import draw_nodes
        draw_nodes(attr, ui)
        page.close(dialog)
        ui.status_text.value = f"Состояние {name} переименовано в {new_name}"
        page.update()

    input_field = TextField(label="Новое имя", value=name, autofocus=True, on_submit=on_submit)
    dialog = AlertDialog(
        title=Text(f"Переименовать {name}"),
        content=input_field,
        actions=[ElevatedButton("OK", on_click=on_submit)]
    )
    return dialog


def edit_transition_dialog(start_name, end_name, attr, ui, page):
    old_symbols = {
        t["symbol"]
        for t in attr.transitions[start_name]
        if t["end"] == end_name
    }

    def on_save(e):
        new_symbols = set(filter(lambda c: c.isalpha() or c == EPSILON_SYMBOL, input_field.value))
        if not new_symbols:
            ui.status_text.value = "Должен быть хотя бы один символ английского алфавита или ε"
            return

        attr.transitions[start_name] = list(filter(lambda t: t["end"] != end_name,
                                                   attr.transitions[start_name]))
        attr.transitions[start_name] += [
            {"symbol": c, "end": end_name}
            for c in new_symbols
        ]
        
        if new_symbols != {EPSILON_SYMBOL}:
            attr.alphabet.update(new_symbols)
            ui.alphabet_display.value = f"Алфавит: {', '.join(attr.alphabet)}"

        from draw import draw_nodes
        draw_nodes(attr, ui)
        
        page.close(dialog)
        ui.status_text.value = f"Переход из {start_name} изменён на '{', '.join(new_symbols)}'"
        page.update()

    def set_epsilon(e):
        input_field.value += EPSILON_SYMBOL
        input_field.focus()
        page.update()

    input_field = TextField(
        label="Символы перехода", 
        value=', '.join(old_symbols),
        width=150,
        autofocus=True,
        on_submit=on_save
    )

    epsilon_btn = ElevatedButton(
        text=EPSILON_SYMBOL, 
        on_click=set_epsilon,
        tooltip="Сделать эпсилон-переходом"
    )

    content_row = Row(
        controls=[input_field, epsilon_btn],
        vertical_alignment="center",
        alignment=MainAxisAlignment.START
    )

    dialog = AlertDialog(
        title=Text(f"Изменить переход {start_name} -> {end_name}"),
        content=content_row,
        actions=[
            ElevatedButton("Сохранить", on_click=on_save)
        ],
    )
    return dialog


def regex_input_dialog(attr, ui, page):
    from automata_operations import import_automaton_data
    from automata.fa.nfa import NFA

    def on_build(e):
        regex_str = input_field.value.strip()
        if not regex_str:
            return
        
        page.close(dialog)
        
        try:
            nfa = NFA.from_regex(regex_str)
        except Exception as ex:
            error_dialog = AlertDialog(
                modal=True,
                title=Text("Ошибка синтаксиса"),
                content=Text(f"Регулярное выражение '{regex_str}' содержит ошибки.\n{ex}"),
                actions=[
                    ElevatedButton("OK", on_click=lambda e: page.close(error_dialog)),
                ],
            )
            page.open(error_dialog)
            ui.status_text.value = f"❌ Ошибка в регулярном выражении"
        else:
            attr.regex = regex_str
            ui.regex_display.value = f"Регулярное выражение: {regex_str}"
            
            if import_automaton_data(nfa, attr, ui):
                from draw import draw_nodes
                draw_nodes(attr, ui)
                ui.status_text.value = f"✅ Автомат построен из: {regex_str}"
            else:
                ui.status_text.value = f"❌ Ошибка при построении"
        
        page.update()

    input_field = TextField(
        label="Регулярное выражение", 
        hint_text="Пример: (a|b)*abb",
        autofocus=True,
        width=400,
        on_submit=on_build
    )
    dialog = AlertDialog(
        modal=True,
        title=Text("Построение автомата из регулярного выражения"),
        content=input_field,
        actions=[
            ElevatedButton("Отмена", on_click=lambda e: page.close(dialog)),
            ElevatedButton("Построить", on_click=on_build),
        ],
        actions_alignment=MainAxisAlignment.END,
    )
    return dialog
