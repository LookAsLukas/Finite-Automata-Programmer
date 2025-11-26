from flet import Text, TextField, ElevatedButton, AlertDialog, Column, Colors

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
    """Создает диалог для ввода регулярного выражения и построения КА"""
    def on_submit(e):
        regex_str = input_field.value.strip()
        if not regex_str:
            ui.status_text.value = "Регулярное выражение не может быть пустым!"
            page.close(dialog)
            page.update()
            return
        
        try:
            # Импортируем здесь чтобы избежать циклического импорта
            from regex_to_fa import regex_to_nfa, validate_regex_syntax
            
            # Сначала проверяем синтаксис регулярного выражения
            is_valid, error_msg = validate_regex_syntax(regex_str)
            if not is_valid:
                ui.status_text.value = f"Неверное регулярное выражение: {error_msg}"
                page.close(dialog)
                page.update()
                return
            
            # Конвертируем регулярное выражение в НКА
            nfa = regex_to_nfa(regex_str)
            
            # Импортируем сгенерированный НКА в UI
            from automata_operations import import_automaton_data
            if import_automaton_data(nfa, attr, ui):
                # ДОБАВЛЕНО: сохраняем и отображаем регулярное выражение
                attr.current_regex = regex_str
                ui.regex_display.value = f"Регулярное выражение: {regex_str}"
                ui.status_text.value = f"✅ КА построен из регулярного выражения: {regex_str}"
                from draw import draw_nodes
                draw_nodes(attr, ui)
            else:
                ui.status_text.value = f"❌ Не удалось построить КА из регулярного выражения: {regex_str}"
                
        except Exception as ex:
            ui.status_text.value = f"❌ Ошибка при построении КА: {str(ex)}"
        
        page.close(dialog)
        page.update()

    input_field = TextField(
        label="Регулярное выражение", 
        hint_text="например: (a|b)*abb, a*b*c*, и т.д.",
        autofocus=True,
        width=400
    )
    
    dialog = AlertDialog(
        modal=True,
        title=Text("Построение КА из регулярного выражения"),
        content=Column([
            Text("Введите регулярное выражение:"),
            input_field,
            Text("Поддерживаемые операторы: конкатенация (ab), альтернация (a|b), звезда Клини (a*)", size=12, color=Colors.GREY),
            Text("Используйте скобки для группировки: (a|b)*", size=12, color=Colors.GREY)
        ], tight=True),
        actions=[
            ElevatedButton("Построить", on_click=on_submit),
            ElevatedButton("Отмена", on_click=lambda e: page.close(dialog)),
        ],
    )
    return dialog