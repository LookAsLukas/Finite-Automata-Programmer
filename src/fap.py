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


def main(page: Page):
    page.title = "FAP"
    page.window_width = 800
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

    word_input = TextField(label="Слово для обработки", hint_text="Введите слово...", width=535)

    drawing_area = canvas.Canvas(width=700, height=450)
    mode_status = Text("Режим размещения: выключен", size=16, color=Colors.GREY_800)
    transition_status = Text("Режим рисования переходов: выключен", size=16, color=Colors.GREY_800)
    status_text = Text("Выберите узел или кликните, чтобы добавить новый узел", size=16, color=Colors.GREY_800)

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

            #ПОДСВЕТКА
            if selected_node == i:
                outline = canvas.Circle(x=x, y=y, radius=30, paint=flet.Paint(Colors.BLUE_800, style="stroke", stroke_width=3))
                elements.append(outline)

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

                arrow_line = canvas.Line(
                    x1=start_x, y1=start_y, x2=end_x, y2=end_y,
                    paint=flet.Paint(Colors.BLACK, stroke_width=2)
                )

                arrow_size = 10
                perp_x, perp_y = -uy, ux
                wing1 = canvas.Line(
                    x1=end_x, y1=end_y,
                    x2=end_x - ux * arrow_size + perp_x * arrow_size,
                    y2=end_y - uy * arrow_size + perp_y * arrow_size,
                    paint=flet.Paint(Colors.BLACK, stroke_width=2)
                )
                wing2 = canvas.Line(
                    x1=end_x, y1=end_y,
                    x2=end_x - ux * arrow_size - perp_x * arrow_size,
                    y2=end_y - uy * arrow_size - perp_y * arrow_size,
                    paint=flet.Paint(Colors.BLACK, stroke_width=2)
                )

                offset = 20 * (trans_list.index(t) + 1)
                label = canvas.Text(
                    x=(start_x + end_x) / 2 + offset,
                    y=(start_y + end_y) / 2 - 10,
                    text=symbol,
                    style=TextStyle(size=18, weight=FontWeight.BOLD)
                )
                elements.extend([arrow_line, wing1, wing2, label])

        drawing_area.shapes.extend(elements)

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
            status_text.value = f"Выбран узел: q{clicked}"

        if transition_mode and clicked is not None:
            if first_selected_node is None:
                first_selected_node = clicked
                transition_status.value = f"Выбрано начальное состояние: q{clicked}"
            else:
                start = f"q{first_selected_node}"
                end = f"q{clicked}"
                transitions.setdefault(start, []).append({"symbol": "a", "end": end})
                first_selected_node = None
                transition_status.value = f"Переход {start} → q{clicked} добавлен"

        draw_nodes()
        page.update()

    def toggle_placing_mode(e):
        nonlocal placing_mode, transition_mode, first_selected_node
        placing_mode = not placing_mode
        if placing_mode:
            transition_mode = False
            first_selected_node = None
        mode_status.value = "Режим размещения: ВКЛЮЧЕН" if placing_mode else "Режим размещения: выключен"
        transition_status.value = "Режим рисования переходов: выключен"
        page.update()

    def toggle_transition_mode(e):
        nonlocal transition_mode, placing_mode, first_selected_node
        transition_mode = not transition_mode
        if transition_mode:
            placing_mode = False
            first_selected_node = None
        transition_status.value = "Режим рисования переходов: ВКЛЮЧЕН" if transition_mode else "Режим рисования переходов: выключен"
        mode_status.value = "Режим размещения: выключен"
        page.update()

    def toggle_start_state(e):
        nonlocal start_state_index
        if transition_mode or placing_mode:
            return
        if selected_node is None:
            status_text.value = "Сначала выберите узел!"
            page.update()
            return
        if start_state_index == selected_node:
            start_state_index = None
            status_text.value = f"q{selected_node} больше не начальное состояние"
        else:
            start_state_index = selected_node
            status_text.value = f"q{selected_node} теперь начальное состояние"
        draw_nodes()
        page.update()

    def toggle_final_state(e):
        nonlocal final_states
        if transition_mode or placing_mode:
            return
        if selected_node is None:
            status_text.value = "Сначала выберите узел!"
            page.update()
            return
        if selected_node in final_states:
            final_states.remove(selected_node)
            status_text.value = f"q{selected_node} больше не конечное состояние"
        else:
            final_states.add(selected_node)
            status_text.value = f"q{selected_node} теперь конечное состояние"
        draw_nodes()
        page.update()

    place_mode_button = ElevatedButton("Переключить режим рисования состояний", on_click=toggle_placing_mode)
    transition_mode_button = ElevatedButton("Переключить режим рисования переходов", on_click=toggle_transition_mode)
    start_button = ElevatedButton("Переключить начальное состояние", on_click=toggle_start_state, width= 500)
    final_button = ElevatedButton("Переключить конечное состояние", on_click=toggle_final_state, width= 500)
    run_button = ElevatedButton("Обработать слово")

    gesture_area = GestureDetector(content=drawing_area, on_tap_down=handle_canvas_click)

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
                            Text("Система обработки ДКА / НКА", size=24, weight="bold"),
                            graph_area,
                            Column([mode_status, transition_status, status_text], spacing=5),
                            Row([word_input, run_button], spacing=20),
                        ],
                        spacing=15,
                    ),
                    padding=20,
                ),
                Container(
                    padding = 60,
                    width=500,
                    content=Column(
                        [
                            Card(
                                content=Container(
                                    content=Column(
                                        [
                                            Text("Режимы", size=18, weight="bold"),
                                            place_mode_button,
                                            transition_mode_button,
                                        ],
                                        spacing=10,
                                    ),
                                    padding=20,
                                    width=500
                                )
                            ),
                            start_button,
                            final_button,
                        ],
                        spacing=20,
                        alignment=MainAxisAlignment.START,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            spacing=5,
            alignment=MainAxisAlignment.START,
            vertical_alignment=CrossAxisAlignment.START,
        )
    )


if __name__ == "__main__":
    flet.app(target=main)
