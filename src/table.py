import flet as ft
from automata_operations import build_nfa_from_ui
from graph import Transition, Node
from application_state import EPSILON_SYMBOL

def open_table_editor(app):
    for node in app.graph.nodes: 
        node.name = str(node.name) 

    states = sorted([nd.name for nd in app.graph.nodes if nd.name != ""], key=str)
    symbols = sorted(app.attr.alphabet)
    has_epsilon = any('' == tr.symbols for tr in app.graph.transitions)
    if has_epsilon:
        symbols.append(EPSILON_SYMBOL)

    cell_fields = {}
    table_holder = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)

    def build_table_ui():
        columns = [ft.DataColumn(ft.Text("Состояние"))] + [ft.DataColumn(ft.Text(sym)) for sym in symbols]
        rows = []
        for state in states:
            cells = [ft.DataCell(ft.Text(state))]
            for sym in symbols:
                nfa_sym = '' if sym == EPSILON_SYMBOL else sym
                targets = map(lambda x: x.end.name,
                              filter(lambda x: x.start.name == state and (nfa_sym in x.symbols or nfa_sym == x.symbols),
                                     app.graph.transitions))
                existing_val = cell_fields.get((state, sym)).value if (state, sym) in cell_fields else ', '.join(str(t) for t in sorted(targets, key=str))
                tf = ft.TextField(
                    value=existing_val,
                    width=100,          
                    height=40,         
                    text_align=ft.TextAlign.CENTER,
                    content_padding=5   
                )
                cell_fields[(state, sym)] = tf
                cells.append(ft.DataCell(ft.Container(content=tf, width=100, height=45)))
            rows.append(ft.DataRow(cells=cells))
        
        table_holder.controls = [
            ft.Row(
                controls=[
                    ft.DataTable(
                        columns=columns,
                        rows=rows,
                        border=ft.border.all(1, "black"),
                        horizontal_lines=ft.border.BorderSide(1, "grey"),
                        vertical_lines=ft.border.BorderSide(1, "grey"),
                        data_row_min_height=60, 
                        data_row_max_height=60, 
                    )
                ],
                scroll=ft.ScrollMode.ADAPTIVE
            )
        ]

    def add_row(e):
        if len(states) >= 10:
            app.page.show_dialog(ft.AlertDialog(title=ft.Text("Лимит достигнут"), content=ft.Text("Максимальное количество состояний: 10")))
            return
        new_name = f"q{len(states)}"
        while new_name in states:
            new_name = f"q{int(new_name[1:]) + 1}"
        states.append(new_name)
        build_table_ui()
        app.page.update()

    def add_column(e):
        if len(symbols) >= 10:
            app.page.show_dialog(ft.AlertDialog(title=ft.Text("Лимит достигнут"), content=ft.Text("Максимальное количество символов: 10")))
            return
        base_syms = [s for s in symbols if s != EPSILON_SYMBOL]
        new_sym = chr(ord(base_syms[-1]) + 1) if base_syms else 'a'
        if EPSILON_SYMBOL in symbols:
            symbols.insert(symbols.index(EPSILON_SYMBOL), new_sym)
        else:
            symbols.append(new_sym)
        build_table_ui()
        app.page.update()

    def apply_changes(e):
        app.history.add(app.graph)
        
        for i, s_name in enumerate(states):
            if not any(n.name == s_name for n in app.graph.nodes):
                new_x = 150 + (i * 50)
                new_y = 150 + (i * 50)
                app.graph.nodes.add(Node(x=new_x, y=new_y, name=s_name))

        new_transitions = set()
        for state in states:
            for sym in symbols:
                tf = cell_fields.get((state, sym))
                if not tf: continue
                raw = tf.value.strip()
                if not raw: continue
                targets = [t.strip() for t in raw.split(',') if t.strip()]
                invalid = [t for t in targets if t not in states]
                if invalid:
                    app.ui.status_text.value = f"Неизвестные состояния: {', '.join(invalid)}"
                    app.page.update()
                    return

        app.graph.transitions.clear()
        pair_symbols = {}
        for state in states:
            for sym in symbols:
                tf = cell_fields.get((state, sym))
                if not tf: continue
                raw = tf.value.strip()
                if not raw: continue
                targets = [t.strip() for t in raw.split(',') if t.strip()]
                nfa_sym = '' if sym == EPSILON_SYMBOL else sym
                for t in targets:
                    pair_symbols.setdefault((state, t), set()).add(nfa_sym)

        for (start_name, end_name), sym_set in pair_symbols.items():
            start_node = next((n for n in app.graph.nodes if n.name == start_name), None)
            end_node = next((n for n in app.graph.nodes if n.name == end_name), None)
            if start_node and end_node:
                symbols_str = ''.join(EPSILON_SYMBOL if s == '' else s for s in sorted(sym_set))
                app.graph.transitions.add(Transition(start=start_node, end=end_node, symbols=symbols_str))

        new_alphabet = {s for s in symbols if s != EPSILON_SYMBOL}
        app.attr.alphabet.update(new_alphabet)
        app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"

        app.draw.redraw()
        app.page.pop_dialog()
        app.ui.status_text.value = "Таблица применена"
        app.page.update()

    build_table_ui()
    dialog = ft.AlertDialog(
        title=ft.Text("Редактор таблицы переходов"),
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Button("Добавить строку", on_click=add_row, icon=ft.Icons.ADD),
                    ft.Button("Добавить столбец", on_click=add_column, icon=ft.Icons.ADD),
                ]),
                ft.Text("Введите целевые состояния через запятую."),
                table_holder,
            ], scroll=ft.ScrollMode.ADAPTIVE, tight=True),
            width=850,
            height=500, 
        ),
        actions=[
            ft.Button("Отмена", on_click=lambda e: app.page.pop_dialog()),
            ft.Button("Применить", on_click=apply_changes),
        ],
    )
    app.page.show_dialog(dialog)
