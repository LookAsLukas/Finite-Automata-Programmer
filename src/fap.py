import math
import flet
from flet import (
    Page,
    Text,
    TextField,
    ElevatedButton,
    Column,
    Row,
    Container,
    Colors,
    alignment,
    CrossAxisAlignment,
    Card,
    MainAxisAlignment,
    canvas,
    GestureDetector,
    TextStyle,
    FontWeight,
    AlertDialog
)
from automata.fa.nfa import NFA
from automata_io import save_automaton_to_json, load_automaton_from_json
from automata_visualizer import prepare_automaton_layout


def main(page: Page):
    page.title = "FAP — Визуальный конструктор НКА"
    page.window_width = 900
    page.window_height = 600
    page.bgcolor = Colors.BLUE_GREY_50

    # nodes: {state_name: (x, y)}
    nodes = {}
    node_counter = 0
    start_state = None
    final_states = set()
    transitions = {}  # {start_state: [{"symbol": "a", "end": "q1"}]}
    selected_node = None
    first_selected_node = None
    placing_mode = False
    transition_mode = False
    alphabet = set()

    # UI элементы
    word_input = TextField(label="Слово для проверки", width=400)
    alphabet_input = TextField(label="Добавить символ", hint_text="Введите один символ...", width=150)
    drawing_area = canvas.Canvas(width=700, height=450)
    mode_status = Text("Режим размещения: выключен", size=16, color=Colors.GREY_800)
    transition_status = Text("Режим переходов: выключен", size=16, color=Colors.GREY_800)
    status_text = Text("Добавьте состояния или переходы", size=16, color=Colors.GREY_800)
    alphabet_display = Text("Алфавит: ∅", size=16, color=Colors.BLUE_800)

        draw_nodes()
        page.update()

    # ---------- Графика ----------
    def draw_nodes():
        elements = []
        for name, (x, y) in nodes.items():
            if name == start_state:
                color = Colors.LIGHT_GREEN_300
            elif name in final_states:
                color = Colors.PINK_200
            else:
                color = Colors.AMBER_100

            circle = canvas.Circle(x=x, y=y, radius=30, paint=flet.Paint(color))
            elements.append(circle)

            if selected_node == name:
                outline = canvas.Circle(
                    x=x, y=y, radius=30,
                    paint=flet.Paint(Colors.BLUE_800, style="stroke", stroke_width=3)
                )
                elements.append(outline)

            text = canvas.Text(
                x=x - 12, y=y - 10,
                text=name,
                style=TextStyle(weight=FontWeight.BOLD)
            )
            elements.append(text)

        drawing_area.shapes = elements
        draw_transitions()
        drawing_area.update()

    def draw_transitions():
        elements = []
        for start, trans_list in transitions.items():
            if start not in nodes:
                continue
            (x1, y1) = nodes[start]

            for t in trans_list:
                symbol = t["symbol"]
                end = t["end"]
                if end not in nodes:
                    continue
                (x2, y2) = nodes[end]
                dx, dy = x2 - x1, y2 - y1
                length = math.sqrt(dx ** 2 + dy ** 2)
                if length == 0:
                    continue
                ux, uy = dx / length, dy / length
                start_x, start_y = x1 + ux * 30, y1 + uy * 30
                end_x, end_y = x2 - ux * 30, y2 - uy * 30

                elements.append(canvas.Line(
                    x1=start_x, y1=start_y, x2=end_x, y2=end_y,
                    paint=flet.Paint(Colors.BLACK, stroke_width=2)
                ))

                arrow_size = 10
                perp_x, perp_y = -uy, ux
                elements.append(canvas.Line(
                    x1=end_x, y1=end_y,
                    x2=end_x - ux * arrow_size + perp_x * arrow_size,
                    y2=end_y - uy * arrow_size + perp_y * arrow_size,
                    paint=flet.Paint(Colors.BLACK, stroke_width=2)
                ))
                elements.append(canvas.Line(
                    x1=end_x, y1=end_y,
                    x2=end_x - ux * arrow_size - perp_x * arrow_size,
                    y2=end_y - uy * arrow_size - perp_y * arrow_size,
                    paint=flet.Paint(Colors.BLACK, stroke_width=2)
                ))

                label = canvas.Text(
                    x=(x1 + x2) / 2 + 10,
                    y=(y1 + y2) / 2 - 10,
                    text=symbol,
                    style=TextStyle(size=18, weight=FontWeight.BOLD)
                )
                elements.append(label)

        return elements

    # ---------- Обработчики ----------
    def add_node(e):
        nonlocal node_counter
        if not placing_mode:
            return
        x, y = e.local_x, e.local_y
        new_name = f"q{node_counter}"
        nodes[new_name] = (x, y)
        node_counter += 1
        draw_nodes()

    def get_clicked_node(x, y):
        for name, (nx, ny) in nodes.items():
            if (x - nx) ** 2 + (y - ny) ** 2 <= 30 ** 2:
                return name
        return None

    def rename_state(name):
        def on_submit(e):
            new_name = input_field.value.strip()
            if not new_name or new_name in nodes:
                status_text.value = "Некорректное или занятое имя!"
                page.close(dialog)
                page.update()
                return

            nodes[new_name] = nodes.pop(name)

            new_transitions = {}
            for s, lst in transitions.items():
                updated_s = new_name if s == name else s
                updated_list = []
                for t in lst:
                    t_copy = t.copy()
                    if t_copy["end"] == name:
                        t_copy["end"] = new_name
                    updated_list.append(t_copy)
                new_transitions[updated_s] = updated_list
            transitions.clear()
            transitions.update(new_transitions)

            nonlocal start_state, selected_node
            if start_state == name:
                start_state = new_name
            if name in final_states:
                final_states.remove(name)
                final_states.add(new_name)
            if selected_node == name:
                selected_node = new_name

            status_text.value = f"Состояние {name} переименовано в {new_name}"
            page.close(dialog)
            draw_nodes()
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

    def handle_canvas_click(e):
        nonlocal first_selected_node, selected_node
        x, y = e.local_x, e.local_y
        clicked = get_clicked_node(x, y)

        if placing_mode:
            add_node(e)
            return

        if transition_mode and clicked is not None:
            if first_selected_node is None:
                first_selected_node = clicked
                transition_status.value = f"Выбрано начальное состояние: {clicked}"
            else:
                start = first_selected_node
                end = clicked
                symbol = next(iter(alphabet)) if alphabet else "a"
                transitions.setdefault(start, []).append({"symbol": symbol, "end": end})
                first_selected_node = None
                transition_status.value = f"Переход {start} → {end} добавлен"
            draw_nodes()
            page.update()
            return

        if not placing_mode and not transition_mode:
            if clicked is not None:
                selected_node = clicked
                status_text.value = f"Выбран узел: {clicked}"
                draw_nodes()
                page.update()

    def get_clicked_transition(x, y):
        threshold = 10  
        for start, trans_list in transitions.items():
            if start not in nodes:
                continue
            (x1, y1) = nodes[start]
            for t in trans_list:
                end = t["end"]
                if end not in nodes:
                    continue
                (x2, y2) = nodes[end]

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

    def edit_transition_symbol(start, transition):
        def on_submit(e):
            new_symbol = input_field.value.strip()
            if not new_symbol:
                status_text.value = "Символ не может быть пустым!"
                page.close(dialog)
                page.update()
                return

            transition["symbol"] = new_symbol
            status_text.value = f"Переход {start} → {transition['end']} изменён на '{new_symbol}'"
            page.close(dialog)
            draw_nodes()
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

    def handle_double_click(e):
        if placing_mode or transition_mode:
            return
        x, y = e.local_x, e.local_y

        clicked_node = get_clicked_node(x, y)
        if clicked_node:
            rename_state(clicked_node)
            return

        start, transition = get_clicked_transition(x, y)
        if transition:
            edit_transition_symbol(start, transition)

    # ---------- Переключатели режимов ----------
    def toggle_placing_mode(e):
        nonlocal placing_mode, transition_mode, first_selected_node
        placing_mode = not placing_mode
        if placing_mode:
            transition_mode = False
            first_selected_node = None
        mode_status.value = "Режим размещения: ВКЛЮЧЕН" if placing_mode else "Режим размещения: выключен"
        page.update()

    def toggle_transition_mode(e):
        nonlocal transition_mode, placing_mode, first_selected_node
        transition_mode = not transition_mode
        if transition_mode:
            placing_mode = False
            first_selected_node = None
        transition_status.value = "Режим переходов: ВКЛЮЧЕН" if transition_mode else "Режим переходов: выключен"
        page.update()

    # ---------- Управление состояниями ----------
    def toggle_start_state(e):
        nonlocal start_state
        if transition_mode or placing_mode:
            return
        if selected_node is None:
            status_text.value = "Выберите узел!"
            page.update()
            return
        if start_state == selected_node:
            start_state = None
            status_text.value = f"{selected_node} больше не начальное состояние"
        else:
            start_state = selected_node
            status_text.value = f"{selected_node} теперь начальное состояние"
        draw_nodes()
        page.update()

    def toggle_final_state(e):
        if transition_mode or placing_mode:
            return
        if selected_node is None:
            status_text.value = "Выберите узел!"
            page.update()
            return
        if selected_node in final_states:
            final_states.remove(selected_node)
            status_text.value = f"{selected_node} больше не конечное состояние"
        else:
            final_states.add(selected_node)
            status_text.value = f"{selected_node} теперь конечное состояние"
        draw_nodes()
        page.update()

    def add_alphabet_symbol(e):
        symbol = alphabet_input.value.strip()
        if symbol and len(symbol) == 1:
            alphabet.add(symbol)
            alphabet_display.value = f"Алфавит: {', '.join(sorted(alphabet))}"
            alphabet_input.value = ""
            status_text.value = f"Добавлен символ '{symbol}'"
        else:
            status_text.value = "Введите один символ!"
        page.update()

    def clear_automaton(e):
        nonlocal nodes, node_counter, start_state, final_states, transitions
        nonlocal selected_node, first_selected_node, placing_mode, transition_mode, alphabet
        
        nodes.clear()
        node_counter = 0
        start_state = None
        final_states.clear()
        transitions.clear()
        selected_node = None
        first_selected_node = None
        placing_mode = False
        transition_mode = False
        alphabet.clear()
        
        drawing_area.shapes = []
        mode_status.value = "Режим размещения: выключен"
        transition_status.value = "Режим рисования переходов: выключен"
        status_text.value = "Автомат очищен"
        alphabet_display.value = "Алфавит: ∅"
        alphabet_input.value = ""
        page.update()

    # ---------- Функции из fapold.py ----------
    def build_nfa_from_ui():
        """Создает объект NFA из automata-lib на основе текущего автомата"""
        if not nodes or start_state is None:
            return None

        states = set(nodes.keys())
        initial_state = start_state
        final_state_names = final_states

        nfa_transitions = {}
        for start_name, trans_list in transitions.items():
            nfa_transitions[start_name] = {}
            for t in trans_list:
                symbol = t["symbol"]
                end_name = t["end"]
                nfa_transitions[start_name].setdefault(symbol, set()).add(end_name)

        for name in states:
            nfa_transitions.setdefault(name, {})

        return NFA(
            states=states,
            input_symbols=set(alphabet),
            transitions=nfa_transitions,
            initial_state=initial_state,
            final_states=final_state_names,
        )

    def handle_run(e):
        """Обработка слова с использованием automata-lib"""
        if start_state is None:
            status_text.value = "Не выбрано начальное состояние!"
            page.update()
            return
        
        nfa = build_nfa_from_ui()
        if nfa is None:
            status_text.value = "Автомат неполный — добавьте состояния!"
            page.update()
            return
        
        word = word_input.value.strip()
        if not word:
            status_text.value = "Введите слово!"
        else:
            try:
                accepted = nfa.accepts_input(word)
                status_text.value = f"Слово '{word}' {'✅ принимается' if accepted else '❌ не принимается'} автоматом"
            except Exception as ex:
                status_text.value = f"Ошибка при обработке слова: {ex}"
        page.update()

    def export_nfa(e):
        """Экспорт автомата в JSON файл"""
        if not nodes:
            status_text.value = "Автомат пуст — нечего экспортировать!"
            page.update()
            return

        if not final_states:
            status_text.value = "Добавьте хотя бы одно конечное состояние!"
            page.update()
            return

        if not alphabet:
            status_text.value = "Алфавит пуст — добавьте символы!"
            page.update()
            return

        if start_state is None:
            status_text.value = "Не выбрано начальное состояние!"
            page.update()
            return

        try:
            nfa = build_nfa_from_ui()
            if nfa is None:
                status_text.value = "Автомат неполный — экспорт невозможен!"
                page.update()
                return
            export_path = "nfa.json"
            save_automaton_to_json(nfa, export_path)
            status_text.value = f"✅ NFA экспортирован в файл {export_path}"
        except (TypeError, IOError) as err:
            status_text.value = f"Ошибка экспорта: {err}"
        page.update()

    def import_automaton(e):
        """Импорт автомата из JSON файла"""
        nonlocal nodes, transitions, final_states, start_state, alphabet, node_counter
        nonlocal placing_mode, transition_mode, selected_node, first_selected_node
        
        automaton = load_automaton_from_json("nfa.json")
        if automaton is None:
            status_text.value = "Не удалось загрузить автомат из nfa.json"
            page.update()
            return

        try:
            layout = prepare_automaton_layout(automaton, canvas_width=700, canvas_height=450)
            layout_nodes, layout_state_names, layout_transitions, layout_final_states, layout_start_index, layout_alphabet = layout

            # Конвертируем формат данных из automata_visualizer в наш формат
            nodes = {}
            for i, (x, y) in enumerate(layout_nodes):
                nodes[layout_state_names[i]] = (x, y)
            
            transitions = {}
            for start_idx, trans_list in layout_transitions.items():
                start_name = layout_state_names[start_idx]
                transitions[start_name] = []
                for t in trans_list:
                    end_name = layout_state_names[t["end"]]
                    transitions[start_name].append({"symbol": t["symbol"], "end": end_name})
            
            final_states = {layout_state_names[i] for i in layout_final_states}
            start_state = layout_state_names[layout_start_index] if layout_start_index is not None else None
            alphabet = set(layout_alphabet)
            node_counter = len(layout_state_names)
            placing_mode = False
            transition_mode = False
            selected_node = None
            first_selected_node = None

            alphabet_display.value = f"Алфавит: {', '.join(sorted(alphabet))}" if alphabet else "Алфавит: ∅"
            mode_status.value = "Режим размещения: выключен"
            transition_status.value = "Режим переходов: выключен"
            status_text.value = "✅ Автомат импортирован из nfa.json"

            draw_nodes()
            page.update()
            
        except Exception as ex:
            status_text.value = f"Ошибка при импорте автомата: {ex}"
            page.update()

    # Кнопки
    place_mode_button = ElevatedButton("Режим добавления состояний", on_click=toggle_placing_mode)
    transition_mode_button = ElevatedButton("Режим добавления переходов", on_click=toggle_transition_mode)
    start_button = ElevatedButton("Переключить начальное состояние", on_click=toggle_start_state)
    final_button = ElevatedButton("Переключить конечное состояние", on_click=toggle_final_state)
    run_button = ElevatedButton("Обработать слово", on_click=handle_run)
    export_button = ElevatedButton("Экспортировать NFA", on_click=export_nfa)
    import_button = ElevatedButton("Импортировать автомат", on_click=import_automaton)
    add_alphabet_button = ElevatedButton("Добавить символ", on_click=add_alphabet_symbol)
    clear_button = ElevatedButton("Очистить автомат", on_click=clear_automaton)

    gesture_area = GestureDetector(
        content=drawing_area,
        on_tap_down=handle_canvas_click,
        on_double_tap_down=handle_double_click
    )

    # ---------- Компоновка ----------
    graph_area = Container(
        bgcolor=Colors.WHITE,
        width=700,
        height=450,
        border_radius=10,
        alignment=alignment.center,
        content=gesture_area,
    )

    page.add(
        Row(
            [
                Container(
                    content=Column(
                        [
                            Text("Визуальный автомат (NFA)", size=24, weight="bold"),
                            graph_area,
                            Column([mode_status, transition_status, status_text], spacing=5),
                            Row([word_input, run_button, export_button, import_button], spacing=10),
                        ],
                        spacing=15,
                    ),
                    padding=20,
                ),
                Container(
                    padding=20,
                    width=350,
                    content=Column(
                        [
                            Card(
                                content=Container(
                                    content=Column(
                                        [Text("Режимы", size=18, weight="bold"), place_mode_button, transition_mode_button],
                                        spacing=10,
                                    ),
                                    padding=10,
                                )
                            ),
                            Card(
                                content=Container(
                                    content=Column(
                                        [Text("Алфавит", size=18, weight="bold"),
                                         Row([alphabet_input, add_alphabet_button], spacing=10),
                                         alphabet_display],
                                        spacing=10,
                                    ),
                                    padding=10,
                                )
                            ),
                            start_button,
                            final_button,
                            clear_button,
                        ],
                        spacing=20,
                        alignment=MainAxisAlignment.START,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            spacing=5,
        )
    )


if __name__ == "__main__":
    flet.app(target=main)