import flet as ft
from automata_operations import build_nfa_from_ui
from graph import Transition
from application_state import EPSILON_SYMBOL

def open_table_editor(app):
    for node in app.graph.nodes: 
        node.name = str(node.name) 
    # Получаем текущий NFA
    nfa = build_nfa_from_ui(app)
    if nfa is None:
        app.ui.status_text.value = "Не удалось построить NFA (нет начальных состояний?)"
        app.page.update()
        return

    # Состояния (все, кроме служебного "")
    states = sorted([s for s in nfa.states if s != ""], key=str)
    # Символы алфавита + ε
    symbols = sorted(app.attr.alphabet)
    has_epsilon = any('' in nfa.transitions.get(s, {}) for s in states)
    if has_epsilon:
        symbols.append(EPSILON_SYMBOL)  # ε

    # Создаём таблицу
    columns = [
        ft.DataColumn(ft.Text("Состояние"))
    ] + [ft.DataColumn(ft.Text(sym)) for sym in symbols]

    rows = []
    # Для хранения ссылок на TextField, чтобы потом прочитать значения
    cell_fields = {}

    for state in states:
        cells = [
            ft.DataCell(ft.Text(state))
        ]
        for sym in symbols:
            # Определяем ключ для NFA: для ε это пустая строка
            nfa_sym = '' if sym == EPSILON_SYMBOL else sym
            targets = nfa.transitions.get(state, {}).get(nfa_sym, set())
            value = ', '.join(str(t) for t in sorted(targets, key=str))
            tf = ft.TextField(value=value, dense=True, width=120)
            # Сохраняем поле, чтобы потом прочитать
            cell_fields[(state, sym)] = tf
            cells.append(ft.DataCell(tf))
        rows.append(ft.DataRow(cells=cells))

    data_table = ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, "black"),
        horizontal_lines=ft.border.BorderSide(1, "grey"),
        vertical_lines=ft.border.BorderSide(1, "grey"),
    )

    # Функция применения изменений
    def apply_changes(e):
        app.history.add(app.graph)
        # Собираем новые переходы
        new_transitions = set()
        for state in states:
            for sym in symbols:
                tf = cell_fields.get((state, sym))
                if not tf:
                    continue
                raw = tf.value.strip()
                if not raw:
                    continue
                # Разбиваем по запятой, убираем лишние пробелы
                targets = [t.strip() for t in raw.split(',') if t.strip()]
                # Проверяем, что все целевые состояния существуют
                invalid = [t for t in targets if t not in states]
                if invalid:
                    app.ui.status_text.value = f"Неизвестные состояния: {', '.join(invalid)}"
                    app.page.update()
                    return
                nfa_sym = '' if sym == EPSILON_SYMBOL else sym
                # Для каждого целевого состояния создаём переход
                for t in targets:
                    # Находим объекты Node по имени (они должны быть в app.graph.nodes)
                    start_node = next((n for n in app.graph.nodes if n.name == state), None)
                    end_node = next((n for n in app.graph.nodes if n.name == t), None)
                    if start_node and end_node:
                        pass
        app.graph.transitions.clear()

        pair_symbols = {}
        for state in states:
            for sym in symbols:
                tf = cell_fields.get((state, sym))
                if not tf:
                    continue
                raw = tf.value.strip()
                if not raw:
                    continue
                targets = [t.strip() for t in raw.split(',') if t.strip()]
                nfa_sym = '' if sym == EPSILON_SYMBOL else sym
                for t in targets:
                    pair = (state, t)
                    pair_symbols.setdefault(pair, set()).add(nfa_sym)

        # Создаём объекты Transition
        for (start_name, end_name), sym_set in pair_symbols.items():
            start_node = next((n for n in app.graph.nodes if n.name == start_name), None)
            end_node = next((n for n in app.graph.nodes if n.name == end_name), None)
            if start_node and end_node:
                # Объединяем символы в строку (для отображения, ε заменяем на символ)
                symbols_str = ''.join(EPSILON_SYMBOL if s == '' else s for s in sorted(sym_set))
                app.graph.transitions.add(Transition(
                    start=start_node,
                    end=end_node,
                    symbols=symbols_str
                ))

        # Обновляем алфавит: добавляем новые символы (кроме ε)
        new_symbols = set()
        for s in symbols:
            if s != EPSILON_SYMBOL:
                new_symbols.add(s)
        app.attr.alphabet.update(new_symbols)
        app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"

        # Перерисовываем граф
        from draw import draw_nodes
        draw_nodes(app)
        app.page.close(dialog)
        app.ui.status_text.value = "Таблица применена"
        app.page.update()

    # Диалог
    dialog = ft.AlertDialog(
        title=ft.Text("Редактор таблицы переходов"),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Введите целевые состояния через запятую. Строка должна соответствовать существующим состояниям."),
                ft.Container(
                    content=data_table,
                    width=800,
                    height=400,
                    padding=10,
                ),
            ], scroll=ft.ScrollMode.ADAPTIVE),
            width=850,
            height=500,
        ),
        actions=[
            ft.ElevatedButton("Отмена", on_click=lambda e: app.page.close(dialog)),
            ft.ElevatedButton("Применить", on_click=apply_changes),
        ],
    )

    app.page.open(dialog)
