import flet
import math
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
    FontWeight
)
from automata.fa.nfa import NFA
from automata_io import save_automaton_to_json


def main(page: Page):
    page.title = "FAP — визуальный конструктор NFA"
    page.window_width = 900
    page.window_height = 600
    page.bgcolor = Colors.BLUE_GREY_50

    nodes = []
    node_counter = 0
    start_state_index = None
    final_states = set()
    transitions = {}
    selected_node = None
    first_selected_node = None
    placing_mode = False
    transition_mode = False
    alphabet = set()

    # --- UI элементы ---
    word_input = TextField(label="Слово для проверки", width=400)
    alphabet_input = TextField(label="Добавить символ", hint_text="Введите один символ...", width=150)
    drawing_area = canvas.Canvas(width=700, height=450)
    mode_status = Text("Режим размещения: выключен", size=16, color=Colors.GREY_800)
    transition_status = Text("Режим переходов: выключен", size=16, color=Colors.GREY_800)
    status_text = Text("Добавьте состояния или переходы", size=16, color=Colors.GREY_800)
    alphabet_display = Text("Алфавит: ∅", size=16, color=Colors.BLUE_800)

    # ---------- Создание объекта NFA ----------
    def build_nfa_from_ui(nodes, transitions, start_state_index, final_states, alphabet):
        states = {f"q{i}" for i in range(len(nodes))}
        initial_state = f"q{start_state_index}" if start_state_index is not None else None
        final_state_names = {f"q{i}" for i in final_states}

        nfa_transitions = {}
        for start, trans_list in transitions.items():
            nfa_transitions[start] = {}
            for t in trans_list:
                symbol = t["symbol"]
                end = t["end"]
                nfa_transitions[start].setdefault(symbol, set()).add(end)

        return NFA(
            states=states,
            input_symbols=set(alphabet),
            transitions=nfa_transitions,
            initial_state=initial_state,
            final_states=final_state_names,
        )

    # ---------- Обработка слова ----------
    def handle_run(e):
        if start_state_index is None:
            status_text.value = "Не выбрано начальное состояние!"
            page.update()
            return
        nfa = build_nfa_from_ui(nodes, transitions, start_state_index, final_states, alphabet)
        word = word_input.value.strip()
        if not word:
            status_text.value = "Введите слово!"
        else:
            accepted = nfa.accepts_input(word)
            status_text.value = f"Слово '{word}' {'✅ принимается' if accepted else '❌ не принимается'} автоматом"
        page.update()

    # ---------- Экспорт автомата ----------
    def export_nfa(e):
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

        if start_state_index is None:
            status_text.value = "Не выбрано начальное состояние!"
            page.update()
            return

        try:
            nfa = build_nfa_from_ui(nodes, transitions, start_state_index, final_states, alphabet)
            export_path = "nfa.json"
            save_automaton_to_json(nfa, export_path)
            status_text.value = f"✅ NFA экспортирован в файл {export_path}"
        except (TypeError, IOError) as err:
            status_text.value = f"Ошибка экспорта: {err}"
        page.update()

    # ---------- Графика ----------
    def draw_nodes():
        elements = []
        for i, (x, y) in enumerate(nodes):
            if i == start_state_index:
                color = Colors.LIGHT_GREEN_300
            elif i in final_states:
                color = Colors.PINK_200
            else:
                color = Colors.AMBER_100

            circle = canvas.Circle(x=x, y=y, radius=30, paint=flet.Paint(color))
            elements.append(circle)
            if selected_node == i:
                elements.append(canvas.Circle(
                    x=x, y=y, radius=30,
                    paint=flet.Paint(Colors.BLUE_800, style="stroke", stroke_width=3)
                ))
            text = canvas.Text(x=x - 8, y=y - 10, text=f"q{i}", style=TextStyle(weight=FontWeight.BOLD))
            elements.append(text)

        drawing_area.shapes = elements
        draw_transitions()
        drawing_area.update()

    def draw_transitions():
        elements = []
        for start, trans_list in transitions.items():
            start_index = int(start.replace("q", ""))
            (x1, y1) = nodes[start_index]
            for t in trans_list:
                symbol = t["symbol"]
                end = t["end"]
                end_index = int(end.replace("q", ""))
                (x2, y2) = nodes[end_index]
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

        drawing_area.shapes.extend(elements)

    # ---------- Обработчики ----------
    def add_node(e):
        nonlocal node_counter
        if not placing_mode:
            return
        x, y = e.local_x, e.local_y
        nodes.append((x, y))
        node_counter += 1
        draw_nodes()

    def get_clicked_node(x, y):
        for i, (nx, ny) in enumerate(nodes):
            if (x - nx) ** 2 + (y - ny) ** 2 <= 30 ** 2:
                return i
        return None

    def handle_canvas_click(e):
        nonlocal first_selected_node, selected_node
        x, y = e.local_x, e.local_y
        if placing_mode:
            add_node(e)
            return
        clicked = get_clicked_node(x, y)
        if clicked is not None:
            selected_node = clicked
            status_text.value = f"Выбран узел q{clicked}"
        if transition_mode and clicked is not None:
            if first_selected_node is None:
                first_selected_node = clicked
                transition_status.value = f"Начало перехода: q{clicked}"
            else:
                start = f"q{first_selected_node}"
                end = f"q{clicked}"
                symbol = next(iter(alphabet)) if alphabet else "a"
                transitions.setdefault(start, []).append({"symbol": symbol, "end": end})
                first_selected_node = None
                transition_status.value = f"Добавлен переход {start} → {end} по '{symbol}'"
        draw_nodes()
        page.update()

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
        nonlocal start_state_index
        if selected_node is None:
            status_text.value = "Выберите узел!"
            page.update()
            return
        if start_state_index == selected_node:
            start_state_index = None
            status_text.value = f"q{selected_node} больше не начальное"
        else:
            start_state_index = selected_node
            status_text.value = f"q{selected_node} теперь начальное"
        draw_nodes()
        page.update()

    def toggle_final_state(e):
        if selected_node is None:
            status_text.value = "Выберите узел!"
            page.update()
            return
        if selected_node in final_states:
            final_states.remove(selected_node)
            status_text.value = f"q{selected_node} больше не конечное"
        else:
            final_states.add(selected_node)
            status_text.value = f"q{selected_node} теперь конечное"
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
        nonlocal node_counter, start_state_index, placing_mode, transition_mode, selected_node, first_selected_node
        nodes.clear()
        node_counter = 0
        transitions.clear()
        final_states.clear()
        alphabet.clear()
        selected_node = None
        first_selected_node = None
        start_state_index = None
        placing_mode = False
        transition_mode = False
        drawing_area.shapes = []
        mode_status.value = "Режим размещения: выключен"
        transition_status.value = "Режим переходов: выключен"
        status_text.value = "Автомат очищен"
        alphabet_display.value = "Алфавит: ∅"
        alphabet_input.value = ""
        page.update()

    # ---------- Кнопки ----------
    place_mode_button = ElevatedButton("Режим добавления состояний", on_click=toggle_placing_mode)
    transition_mode_button = ElevatedButton("Режим добавления переходов", on_click=toggle_transition_mode)
    start_button = ElevatedButton("Переключить начальное состояние", on_click=toggle_start_state)
    final_button = ElevatedButton("Переключить конечное состояние", on_click=toggle_final_state)
    run_button = ElevatedButton("Обработать слово", on_click=handle_run)
    export_button = ElevatedButton("Экспортировать NFA", on_click=export_nfa)
    add_alphabet_button = ElevatedButton("Добавить символ", on_click=add_alphabet_symbol)
    clear_button = ElevatedButton("Очистить автомат", on_click=clear_automaton)

    gesture_area = GestureDetector(content=drawing_area, on_tap_down=handle_canvas_click)

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
                            Row([word_input, run_button, export_button], spacing=10),
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
