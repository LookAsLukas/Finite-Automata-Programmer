import flet as ft
from automata_operations import build_nfa_from_ui
from graph import Transition, Node, NodeType
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

        self.state_types = {
            node.name: node.type
            for node in app.graph.nodes
        }

        self.table_holder = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
        self.table_sheet = None

    def get_states(self):
        return sorted([str(nd.name) for nd in self.app.graph.nodes if nd.name != ""], key=str)

    def get_symbols(self):
        syms = sorted(list(self.app.attr.alphabet))
        has_epsilon = False
        for tr in self.app.graph.transitions:
            if EPSILON_SYMBOL in tr.symbols or tr.symbols == '':
                has_epsilon = True
                break
        if has_epsilon and EPSILON_SYMBOL not in syms:
            syms.append(EPSILON_SYMBOL)
        return syms

    def get_transition_map(self):
        tr_map = {}
        for tr in self.app.graph.transitions:
            start_name = str(tr.start.name)
            if not start_name: continue 
            
            for sym in tr.symbols:
                ui_sym = EPSILON_SYMBOL if sym == '' else sym
                key = (start_name, ui_sym)
                if key not in tr_map:
                    tr_map[key] = set()
                tr_map[key].add(str(tr.end.name))
        return tr_map

    def get_state_marker(self, state):
        node_type = self.state_types.get(state, NodeType.NORMAL)

        if node_type == NodeType.START:
            return "→"

        if node_type == NodeType.FINAL:
            return "←"

        if node_type == NodeType.START_FINAL:
            return "↔"

        return ""

    def cycle_state_type(self, state):
        current = self.state_types.get(state, NodeType.NORMAL)

        if current == NodeType.NORMAL:
            self.state_types[state] = NodeType.START

        elif current == NodeType.START:
            self.state_types[state] = NodeType.FINAL

        elif current == NodeType.FINAL:
            self.state_types[state] = NodeType.START_FINAL

        else:
            self.state_types[state] = NodeType.NORMAL

        self.refresh_ui()

    def _redraw_canvas(self):
        """Перерисовать канвас без закрытия таблицы."""
        try:
            from draw import draw_nodes
            draw_nodes(self.app)
        except Exception:
            pass
        self.app.page.update()

    def build_table_ui(self):
        states = self.states
        symbols = self.symbols
        tr_map = self.get_transition_map()
        
        COLOR_HEADER_BG = ft.Colors.BLUE_GREY_50     
        COLOR_HEADER_TEXT = ft.Colors.BLUE_900       
        COLOR_STATE_TEXT = ft.Colors.BLUE_GREY_900    
        COLOR_MARKER = ft.Colors.ORANGE_ACCENT_700    
        
        COLOR_TF_TEXT = ft.Colors.BLACK             
        COLOR_TF_BG = ft.Colors.GREY_100             
        COLOR_TF_BORDER = ft.Colors.GREY_400          
        COLOR_TF_FOCUS_BORDER = ft.Colors.BLUE_500    
        
        columns = [
            ft.DataColumn(ft.Text("Тип", weight=ft.FontWeight.BOLD, color=COLOR_HEADER_TEXT)),
            ft.DataColumn(ft.Text("Состояние", weight=ft.FontWeight.BOLD, color=COLOR_HEADER_TEXT))
        ] + [
            ft.DataColumn(
                ft.GestureDetector(
                    content=ft.Text(sym, weight=ft.FontWeight.BOLD, color=COLOR_HEADER_TEXT),
                    on_double_tap=lambda e, s=sym: self.edit_label(False, s)
                )
            ) for sym in symbols
        ]

        rows = []
        for state in states:
            cells = [
                ft.DataCell(
                    ft.GestureDetector(
                        content=ft.Container(
                            content=ft.Text(
                                self.get_state_marker(state),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_MARKER, 
                            ),
                            alignment=ft.alignment.center,
                            width=40,
                        ),
                        on_tap=lambda e, s=state: self.cycle_state_type(s)
                    )
                ),

                ft.DataCell(
                    ft.GestureDetector(
                        content=ft.Text(state, weight=ft.FontWeight.BOLD, color=COLOR_STATE_TEXT),
                        on_double_tap=lambda e, s=state: self.edit_label(True, s)
                    )
                )
            ]
            
            for sym in symbols:
                targets = tr_map.get((state, sym), set())
                existing_val = ", ".join(sorted(targets, key=str))
                
                if (state, sym) in self.cell_fields:
                    existing_val = self.cell_fields[(state, sym)].value

                tf = ft.TextField(
                    value=existing_val,
                    width=100,
                    height=40,
                    text_align=ft.TextAlign.CENTER,
                    content_padding=5,
                    color=COLOR_TF_TEXT,
                    bgcolor=COLOR_TF_BG,
                    border_color=COLOR_TF_BORDER,
                    focused_border_color=COLOR_TF_FOCUS_BORDER,
                    cursor_color=COLOR_TF_TEXT,
                )

                self.cell_fields[(state, sym)] = tf

                cells.append(
                    ft.DataCell(
                        ft.Container(
                            content=tf,
                            width=100,
                            height=45
                        )
                    )
                )
            
            rows.append(ft.DataRow(cells=cells))

        self.table_holder.controls = [
            ft.Row([
                ft.DataTable(
                    columns=columns, 
                    rows=rows,
                    border=ft.border.all(1, "#EEEEEE"),
                    horizontal_lines=ft.border.BorderSide(1, "#EEEEEE"),
                    vertical_lines=ft.border.BorderSide(1, "#EEEEEE"),
                    heading_row_color=COLOR_HEADER_BG, 
                )
            ], scroll=ft.ScrollMode.ADAPTIVE)
        ]

    def edit_label(self, is_row, old_val):
        edit_tf = ft.TextField(value=old_val, autofocus=True)

        def save_label(e):
            new_val = edit_tf.value.strip()

            if not new_val or new_val == old_val:
                self.app.page.close(edit_dialog)
                return

            self.app.history.add(self.app.graph)

            if is_row:
                # Rename state in local list
                if old_val in self.states:
                    idx = self.states.index(old_val)
                    self.states[idx] = new_val

                # Move cell_fields keys
                new_cell_fields = {}
                for (s, sym), tf in self.cell_fields.items():
                    new_s = new_val if s == old_val else s
                    new_cell_fields[(new_s, sym)] = tf
                self.cell_fields = new_cell_fields

                # Move state_types
                if old_val in self.state_types:
                    self.state_types[new_val] = self.state_types.pop(old_val)

                # Rename in the actual graph node
                node = next((n for n in self.app.graph.nodes if str(n.name) == old_val), None)
                if node:
                    node.name = new_val

            else:
                # Rename symbol in local list
                if old_val in self.symbols:
                    idx = self.symbols.index(old_val)
                    self.symbols[idx] = new_val

                # Move cell_fields keys
                new_cell_fields = {}
                for (s, sym), tf in self.cell_fields.items():
                    new_sym = new_val if sym == old_val else sym
                    new_cell_fields[(s, new_sym)] = tf
                self.cell_fields = new_cell_fields

                # Update alphabet
                if old_val in self.app.attr.alphabet:
                    self.app.attr.alphabet.discard(old_val)
                    self.app.attr.alphabet.add(new_val)

                # Rename symbols in transitions
                for tr in self.app.graph.transitions:
                    if old_val in tr.symbols:
                        tr.symbols = tr.symbols.replace(old_val, new_val)

            self.app.page.close(edit_dialog)
            self._redraw_canvas()
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
        if len(self.states) >= 10:
            return

        new_name = f"q{len(self.states)}"

        while new_name in self.states:
            new_name = f"q{int(new_name[1:]) + 1 if new_name[1:].isdigit() else len(self.states)}"

        self.states.append(new_name)
        self.state_types[new_name] = NodeType.NORMAL

        self.refresh_ui()

    def delete_row(self, e):
        if self.states:
            last = self.states.pop()

            keys_to_del = [k for k in self.cell_fields if k[0] == last]
            for k in keys_to_del:
                self.cell_fields.pop(k)

            if last in self.state_types:
                self.state_types.pop(last)

            self.refresh_ui()

    def add_column(self, e):
        if len(self.symbols) >= 10:
            return

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
            for k in keys_to_del:
                self.cell_fields.pop(k)

            self.refresh_ui()

    def apply_changes(self, e):
        self.app.history.add(self.app.graph)

        # Validate targets
        for state in self.states:
            for sym in self.symbols:
                tf = self.cell_fields.get((state, sym))
                if not tf or not tf.value.strip():
                    continue
                targets = [t.strip() for t in tf.value.split(',') if t.strip()]
                invalid = [t for t in targets if t not in self.states]
                if invalid:
                    self.app.ui.status_text.value = f"Ошибка: {invalid[0]} не существует"
                    self.app.page.update()
                    return

        current_node_names = {n.name for n in self.app.graph.nodes}

        for i, s_name in enumerate(self.states):
            if s_name not in current_node_names:
                self.app.graph.nodes.add(
                    Node(
                        x=150 + i * 30,
                        y=150 + i * 30,
                        name=s_name,
                        type=self.state_types.get(s_name, NodeType.NORMAL)
                    )
                )

        for node in self.app.graph.nodes:
            if node.name in self.state_types:
                node.type = self.state_types[node.name]

        self.app.graph.transitions.clear()

        pair_symbols = {}

        for state in self.states:
            for sym in self.symbols:
                tf = self.cell_fields.get((state, sym))
                if not tf or not tf.value.strip():
                    continue

                nfa_sym = '' if sym == EPSILON_SYMBOL else sym
                targets = [t.strip() for t in tf.value.split(',') if t.strip()]

                for t in targets:
                    pair_symbols.setdefault((state, t), set()).add(nfa_sym)

        for (start_n, end_n), sym_set in pair_symbols.items():
            start_node = next((n for n in self.app.graph.nodes if n.name == start_n), None)
            end_node = next((n for n in self.app.graph.nodes if n.name == end_n), None)
            if not start_node or not end_node:
                continue

            symbols_str = "".join(sorted(sym_set))
            self.app.graph.transitions.add(
                Transition(start=start_node, end=end_node, symbols=symbols_str)
            )

        self.app.attr.alphabet = {s for s in self.symbols if s != EPSILON_SYMBOL}

        from draw import draw_nodes
        draw_nodes(self.app)

        self.app.page.close(self.table_sheet)

        self.app.ui.status_text.value = "Таблица применена"
        self.app.page.update()

    def refresh_ui(self):
        self.build_table_ui()

        if self.table_holder:
            self.table_holder.update()

    def open(self):
        self.build_table_ui()

        self.table_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20, bgcolor=ft.Colors.WHITE,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Редактор таблицы", size=20, weight="bold", color = "black"),
                        ft.IconButton(
                            ft.Icons.CLOSE,
                            on_click=lambda _: self.app.page.close(self.table_sheet)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.ElevatedButton("Строка", on_click=self.add_row, icon=ft.Icons.ADD),
                        ft.ElevatedButton("Строка", on_click=self.delete_row, icon=ft.Icons.REMOVE, bgcolor=ft.Colors.RED_50),
                        ft.VerticalDivider(),
                        ft.ElevatedButton("Столбец", on_click=self.add_column, icon=ft.Icons.ADD_CIRCLE),
                        ft.ElevatedButton("Столбец", on_click=self.delete_column, icon=ft.Icons.REMOVE_CIRCLE, bgcolor=ft.Colors.RED_50),
                        ft.VerticalDivider(),
                        ft.ElevatedButton(
                            "Применить",
                            on_click=self.apply_changes,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE
                        ),
                    ], wrap=True),
                    ft.Text(
                        "Подсказка: Дважды кликни на состояние или символ, чтобы переименовать. Кликни на тип — сменить роль состояния.",
                        size=13, weight="bold", color="green"
                    ),
                    ft.Divider(),
                    self.table_holder,
                ], scroll=ft.ScrollMode.ADAPTIVE, tight=True),
                height=CHELKA,
            ),
            is_scroll_controlled=True
        )

        self.app.page.open(self.table_sheet)


def open_table_editor(app):
    editor = TableEditor(app)
    editor.open()