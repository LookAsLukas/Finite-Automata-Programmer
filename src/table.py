import flet as ft
from automata_operations import build_nfa_from_ui
from graph import Transition, Node
from application_state import EPSILON_SYMBOL

CHELKA = 450 

class TableEditor:
    def __init__(self, app):
        self.app = app
        self.states = sorted([str(nd.name) for nd in app.graph.nodes if nd.name != ""], key=str)
        self.symbols = sorted(list(app.attr.alphabet))
        
        has_epsilon = any('' == tr.symbols for tr in app.graph.transitions)
        if has_epsilon and EPSILON_SYMBOL not in self.symbols:
            self.symbols.append(EPSILON_SYMBOL)

        self.cell_fields = {}
        self.table_holder = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
        self.table_sheet = None

    def get_transition_map(self):
        """Оптимизированный сбор переходов в словарь."""
        tr_map = {}
        for tr in self.app.graph.transitions:
            start_name = str(tr.start.name)
            syms_in_transition = ['' if s == '' else s for s in tr.symbols] if isinstance(tr.symbols, (list, set)) else [tr.symbols]
            
            for sym in syms_in_transition:
                ui_sym = EPSILON_SYMBOL if sym == '' else sym
                key = (start_name, ui_sym)
                if key not in tr_map:
                    tr_map[key] = set()
                tr_map[key].add(str(tr.end.name))
        return tr_map

    def build_table_ui(self):
        """Отрисовка таблицы без подсказок."""
        tr_map = self.get_transition_map()
        
        columns = [ft.DataColumn(ft.Text("Состояние"))] + [
            ft.DataColumn(
                ft.GestureDetector(
                    content=ft.Text(sym, weight=ft.FontWeight.BOLD),
                    on_double_tap=lambda e, s=sym: self.edit_label(False, s)
                )
            ) for sym in self.symbols
        ]

        rows = []
        for state in self.states:
            cells = [
                ft.DataCell(
                    ft.GestureDetector(
                        content=ft.Text(state, weight=ft.FontWeight.BOLD),
                        on_double_tap=lambda e, s=state: self.edit_label(True, s)
                    )
                )
            ]
            
            for sym in self.symbols:
                targets = tr_map.get((state, sym), [])
                existing_val = ", ".join(sorted(targets, key=str))
                
                if (state, sym) in self.cell_fields:
                    existing_val = self.cell_fields[(state, sym)].value

                tf = ft.TextField(
                    value=existing_val,
                    # hint_text удален
                    width=100,
                    height=40,
                    text_align=ft.TextAlign.CENTER,
                    content_padding=5
                )
                self.cell_fields[(state, sym)] = tf
                cells.append(ft.DataCell(ft.Container(content=tf, width=100, height=45)))
            
            rows.append(ft.DataRow(cells=cells))

        self.table_holder.controls = [
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

    def edit_label(self, is_row, old_val):
        edit_tf = ft.TextField(value=old_val, autofocus=True)
        
        def save_label(e):
            new_val = edit_tf.value.strip()
            if not new_val: return
            
            if is_row:
                idx = self.states.index(old_val)
                self.states[idx] = new_val
                for sym in self.symbols:
                    if (old_val, sym) in self.cell_fields:
                        self.cell_fields[(new_val, sym)] = self.cell_fields.pop((old_val, sym))
            else:
                idx = self.symbols.index(old_val)
                self.symbols[idx] = new_val
                for state in self.states:
                    if (state, old_val) in self.cell_fields:
                        self.cell_fields[(state, new_val)] = self.cell_fields.pop((state, old_val))
            
            self.app.page.close(edit_dialog)
            self.refresh_ui()

        edit_dialog = ft.AlertDialog(
            title=ft.Text(f"Переименовать {'состояние' if is_row else 'символ'}"),
            content=edit_tf,
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: self.app.page.close(edit_dialog)),
                ft.ElevatedButton("Сохранить", on_click=save_label)
            ],
        )
        self.app.page.open(edit_dialog)

    def add_row(self, e):
        if len(self.states) >= 10: return
        new_name = f"q{len(self.states)}"
        while new_name in self.states:
            new_name = f"q{int(new_name[1:]) + 1 if new_name[1:].isdigit() else len(self.states)}"
        self.states.append(new_name)
        self.refresh_ui()

    def delete_row(self, e):
        if self.states:
            last = self.states.pop()
            keys_to_del = [k for k in self.cell_fields if k[0] == last]
            for k in keys_to_del: self.cell_fields.pop(k)
            self.refresh_ui()

    def add_column(self, e):
        if len(self.symbols) >= 10: return
        base_syms = [s for s in self.symbols if s != EPSILON_SYMBOL]
        new_sym = chr(ord(base_syms[-1]) + 1) if base_syms else 'a'
        if EPSILON_SYMBOL in self.symbols:
            self.symbols.insert(self.symbols.index(EPSILON_SYMBOL), new_sym)
        else:
            self.symbols.append(new_sym)
        self.refresh_ui()

    def delete_column(self, e):
        if self.symbols:
            last = self.symbols.pop()
            keys_to_del = [k for k in self.cell_fields if k[1] == last]
            for k in keys_to_del: self.cell_fields.pop(k)
            self.refresh_ui()

    def apply_changes(self, e):
        self.app.history.add(self.app.graph)
        
        for state in self.states:
            for sym in self.symbols:
                tf = self.cell_fields.get((state, sym))
                if not tf or not tf.value.strip(): continue
                targets = [t.strip() for t in tf.value.split(',') if t.strip()]
                invalid = [t for t in targets if t not in self.states]
                if invalid:
                    self.app.ui.status_text.value = f"Ошибка: {invalid[0]} не существует"
                    self.app.page.update()
                    return

        current_node_names = {n.name for n in self.app.graph.nodes}
        for i, s_name in enumerate(self.states):
            if s_name not in current_node_names:
                self.app.graph.nodes.add(Node(x=150 + i*30, y=150 + i*30, name=s_name))

        self.app.graph.transitions.clear()
        pair_symbols = {}
        for state in self.states:
            for sym in self.symbols:
                tf = self.cell_fields.get((state, sym))
                if not tf or not tf.value.strip(): continue
                
                nfa_sym = '' if sym == EPSILON_SYMBOL else sym
                targets = [t.strip() for t in tf.value.split(',') if t.strip()]
                for t in targets:
                    pair_symbols.setdefault((state, t), set()).add(nfa_sym)

        for (start_n, end_n), sym_set in pair_symbols.items():
            start_node = next(n for n in self.app.graph.nodes if n.name == start_n)
            end_node = next(n for n in self.app.graph.nodes if n.name == end_n)
            symbols_str = "".join(sorted(sym_set))
            self.app.graph.transitions.add(Transition(start=start_node, end=end_node, symbols=symbols_str))

        self.app.attr.alphabet = {s for s in self.symbols if s != EPSILON_SYMBOL}
        from draw import draw_nodes
        draw_nodes(self.app)
        self.app.page.close(self.table_sheet)
        self.app.ui.status_text.value = "Таблица применена"
        self.app.page.update()

    def refresh_ui(self):
        self.build_table_ui()
        self.app.page.update()

    def open(self):
        self.build_table_ui()
        self.table_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Редактор таблицы", size=20, weight="bold"),
                        ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.app.page.close(self.table_sheet))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Row([
                        ft.ElevatedButton("Строка +", on_click=self.add_row, icon=ft.Icons.ADD),
                        ft.ElevatedButton("Строка -", on_click=self.delete_row, icon=ft.Icons.REMOVE, bgcolor=ft.Colors.RED_50),
                        ft.VerticalDivider(),
                        ft.ElevatedButton("Столбец +", on_click=self.add_column, icon=ft.Icons.ADD_CIRCLE),
                        ft.ElevatedButton("Столбец -", on_click=self.delete_column, icon=ft.Icons.REMOVE_CIRCLE, bgcolor=ft.Colors.RED_50),
                        ft.VerticalDivider(),
                        ft.ElevatedButton("Применить", on_click=self.apply_changes, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                    ], wrap=True),
                    
                    self.table_holder,
                ], scroll=ft.ScrollMode.ADAPTIVE, tight=True),
                height=CHELKA,
            )
        )
        self.app.page.open(self.table_sheet)

def open_table_editor(app):
    editor = TableEditor(app)
    editor.open()