import flet as ft
from graph import Transition, Node
from application_state import EPSILON_SYMBOL

CHELKA = 450 

class TableEditor:
    def __init__(self, app):
        self.app = app
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

    def build_table_ui(self):
        states = self.get_states()
        symbols = self.get_symbols()
        tr_map = self.get_transition_map()
        
        columns = [ft.DataColumn(ft.Text("Состояние", weight="bold", color = "black"))] + [
            ft.DataColumn(
                ft.GestureDetector(
                    content=ft.Text(sym, weight=ft.FontWeight.BOLD, color="blue"),
                    on_double_tap=lambda e, s=sym: self.edit_label(False, s)
                )
            ) for sym in symbols
        ]

        rows = []
        for state in states:
            cells = [
                ft.DataCell(
                    ft.GestureDetector(
                        content=ft.Text(state, weight=ft.FontWeight.BOLD, color="blue"),
                        on_double_tap=lambda e, s=state: self.edit_label(True, s)
                    )
                )
            ]
            
            for sym in symbols:
                targets = tr_map.get((state, sym), [])
                existing_val = ", ".join(sorted(targets, key=str))

                cells.append(
                    ft.DataCell(
                        ft.GestureDetector(
                            content=ft.Container(
                                content=ft.Text(existing_val if existing_val else "—", color="black" if existing_val else "grey"),
                                width=100, height=45, alignment=ft.alignment.center,
                                bgcolor="#f8fafc" if existing_val else "white",
                                border_radius=5
                            ),
                            on_double_tap=lambda e, sf=state, sm=sym, ev=existing_val: self.edit_cell(sf, sm, ev)
                        )
                    )
                )
            
            rows.append(ft.DataRow(cells=cells))

        self.table_holder.controls = [
            ft.Row([
                ft.DataTable(
                    columns=columns, rows=rows,
                    border=ft.border.all(1, "#EEEEEE"),
                    horizontal_lines=ft.border.BorderSide(1, "#EEEEEE"),
                    vertical_lines=ft.border.BorderSide(1, "#EEEEEE"),
                )
            ], scroll=ft.ScrollMode.ADAPTIVE)
        ]

    def edit_cell(self, state_from, symbol, current_val):
        edit_tf = ft.TextField(value=current_val, autofocus=True, label=f"Куда ведет '{symbol}' из {state_from}?")
        
        def save_cell(e):
            new_val = edit_tf.value.strip()
            self.app.history.add(self.app.graph)
            
            start_node = next((n for n in self.app.graph.nodes if str(n.name) == state_from), None)
            if not start_node: return

            for tr in list(self.app.graph.transitions):
                if tr.start == start_node:
                    if symbol in tr.symbols:
                        tr.symbols = tr.symbols.replace(symbol, "")
                    elif symbol == EPSILON_SYMBOL and tr.symbols == '':
                        tr.symbols = ''
                    
                    if not tr.symbols:
                        self.app.graph.transitions.remove(tr)

            if new_val and new_val not in ["-", "—"]:
                targets = [t.strip() for t in new_val.split(",") if t.strip()]
                for t_name in targets:
                    end_node = next((n for n in self.app.graph.nodes if str(n.name) == t_name), None)
                    if not end_node:
                        self.app.ui.status_text.value = f"Ошибка: Состояния '{t_name}' не существует"
                        self.app.page.update()
                        continue
                        
                    existing_tr = next((tr for tr in self.app.graph.transitions if tr.start == start_node and tr.end == end_node), None)
                    if existing_tr:
                        if symbol not in existing_tr.symbols:
                            existing_tr.symbols += symbol
                    else:
                        self.app.graph.transitions.add(Transition(start=start_node, end=end_node, symbols=symbol))
            
            self.app.page.close(edit_dialog)
            self.update_canvas()
            self.refresh_ui()

        edit_dialog = ft.AlertDialog(
            title=ft.Text("Изменить переходы (цели через запятую)"),
            content=edit_tf,
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: self.app.page.close(edit_dialog)),
                ft.ElevatedButton("Сохранить", on_click=save_cell)
            ],
        )
        self.app.page.open(edit_dialog)

    def edit_label(self, is_row, old_val):
        edit_tf = ft.TextField(value=old_val, autofocus=True)
        
        def save_label(e):
            new_val = edit_tf.value.strip()
            if not new_val or new_val == old_val:
                self.app.page.close(edit_dialog)
                return
            
            self.app.history.add(self.app.graph)

            if is_row:
                states = self.get_states()
                if new_val in states: 
                    self.app.page.close(edit_dialog)
                    return
                node = next((n for n in self.app.graph.nodes if str(n.name) == old_val), None)
                if node: node.name = new_val
            else:
                symbols = self.get_symbols()
                if new_val in symbols: 
                    self.app.page.close(edit_dialog)
                    return
                
                if old_val in self.app.attr.alphabet:
                    self.app.attr.alphabet.remove(old_val)
                self.app.attr.alphabet.add(new_val)
                
                real_old = '' if old_val == EPSILON_SYMBOL else old_val
                real_new = '' if new_val == EPSILON_SYMBOL else new_val
                
                for tr in self.app.graph.transitions:
                    if real_old in tr.symbols:
                        tr.symbols = tr.symbols.replace(real_old, real_new)

            self.app.page.close(edit_dialog)
            self.update_canvas()
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
        states = self.get_states()
        new_name = f"q{len(states)}"
        while new_name in states:
            new_name = f"q{int(new_name[1:]) + 1 if any(c.isdigit() for c in new_name) else len(states)}"
        
        self.app.history.add(self.app.graph)
        from graph import Node
        self.app.graph.nodes.add(Node(x=100 + len(states)*50, y=100 + len(states)*50, name=new_name))
        self.update_canvas()
        self.refresh_ui()

    def delete_row(self, e):
        states = self.get_states()
        if states:
            last = states[-1]
            self.app.history.add(self.app.graph)
            
            node_to_del = next((n for n in self.app.graph.nodes if str(n.name) == last), None)
            if node_to_del:
                self.app.graph.nodes.remove(node_to_del)
                for tr in list(self.app.graph.transitions):
                    if tr.start == node_to_del or tr.end == node_to_del:
                        self.app.graph.transitions.remove(tr)
                        
            self.update_canvas()
            self.refresh_ui()

    def add_column(self, e):
        symbols = self.get_symbols()
        base_syms = [s for s in symbols if s != EPSILON_SYMBOL]
        new_sym = chr(ord(base_syms[-1]) + 1) if base_syms else 'a'
        if new_sym not in self.app.attr.alphabet:
            self.app.attr.alphabet.add(new_sym)
            self.update_canvas()
            self.refresh_ui()

    def delete_column(self, e):
        symbols = self.get_symbols()
        if symbols:
            last = symbols[-1]
            if last == EPSILON_SYMBOL: return
            
            self.app.history.add(self.app.graph)
            if last in self.app.attr.alphabet:
                self.app.attr.alphabet.remove(last)
                
            for tr in list(self.app.graph.transitions):
                if last in tr.symbols:
                    tr.symbols = tr.symbols.replace(last, "")
                    if not tr.symbols:
                        self.app.graph.transitions.remove(tr)
                        
            self.update_canvas()
            self.refresh_ui()

    def update_canvas(self):
        if self.app.attr.alphabet:
             self.app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(self.app.attr.alphabet))}"
        import draw
        res = draw.draw_nodes(self.app)
        if isinstance(res, list):
            self.app.ui.drawing_area.shapes.clear()
            self.app.ui.drawing_area.shapes.extend(res)
        self.app.page.update()

    def refresh_ui(self):
        self.build_table_ui()
        self.app.page.update()

    def open(self):
        self.build_table_ui()
        self.table_sheet = ft.BottomSheet(
            content=ft.Container(
                padding=20, bgcolor=ft.Colors.WHITE,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Редактор таблицы", size=20, weight="bold", color="black"),
                        ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.app.page.close(self.table_sheet))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.ElevatedButton("Состояние ", on_click=self.add_row, icon=ft.Icons.ADD, color="white", bgcolor="blue"),
                        ft.ElevatedButton("Состояние ", on_click=self.delete_row, icon=ft.Icons.REMOVE, color="red"),
                        ft.VerticalDivider(),
                        ft.ElevatedButton("Символ ", on_click=self.add_column, icon=ft.Icons.ADD, color="white", bgcolor="blue"),
                        ft.ElevatedButton("Символ ", on_click=self.delete_column, icon=ft.Icons.REMOVE, color="red"),
                    ], wrap=True),
                    ft.Text("Подсказка: Дважды кликни на любую ячейку, чтобы изменить целевые переходы!", size=13, weight="bold", color="green"),
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