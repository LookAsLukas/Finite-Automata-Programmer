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
    TextStyle, FontWeight
)


def main(page: Page):
    page.title = "FAP"
    page.window_width = 800
    page.window_height = 500
    page.bgcolor = Colors.BLUE_GREY_50

    nodes = []
    node_counter = 0

    #СЛОВАРЬ ДЛЯ ПЕРЕХОДОВ
    transitions = {} 

    word_input = TextField(
        label="Слово для обработки",
        hint_text="Введите слово...",
        width=535,
    )

    start_state_input = TextField(label="Стартовое состояние", width=300)
    end_state_input = TextField(label="Финишное состояние", width=300)
    symbol_input = TextField(label="Буква перехода", width=300)
    


    drawing_area = canvas.Canvas(width=700, height=450)

    def draw_nodes():
        elements = []
        for i, (x, y) in enumerate(nodes):
            circle = canvas.Circle(
                x=x,
                y=y,
                radius=30,
                paint=flet.Paint(Colors.AMBER_100)
            )
            elements.append(circle)

            text = canvas.Text(
                x=x-8,
                y=y-10,
                text = 'q' + str(i)
            )
            elements.append(text)
        
    
        drawing_area.shapes = elements
        drawing_area.update()

    def add_node(e):
        nonlocal node_counter
        x = e.local_x
        y = e.local_y
        print(f"Clicked at: {x}, {y}")
        nodes.append((x, y))
        draw_nodes()
        node_counter += 1

    def add_transition(e):
        """СТРЕЛКИ"""
        start = start_state_input.value.strip()
        end = end_state_input.value.strip()
        symbol = symbol_input.value.strip()

        start_index = int(start.replace("q", ""))
        end_index = int(end.replace("q", ""))
        #КООРДИНАТЫ ДЛЯ СТРЕЛОК ПО СООТВ НОДЕ
        (x1, y1) = nodes[start_index]
        (x2, y2) = nodes[end_index]

        #ДОБАВЛЕНИЕ ТРАНЗИШНА В СЛОВАРЬ
        if start not in transitions:
            transitions[start] = {}
        transitions[start][symbol] = end
        print("Текущие переходы:", transitions)

        # РИСОВАНИЕ СТРЕЛКИ 
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx ** 2 + dy ** 2)
        ux, uy = dx / length, dy / length  
        start_x = x1 + ux * 30
        start_y = y1 + uy * 30
        end_x = x2 - ux * 30
        end_y = y2 - uy * 30

        arrow_line = canvas.Line(x1=start_x, y1=start_y, x2=end_x, y2=end_y, paint=flet.Paint(Colors.BLACK, stroke_width=2))
        
        # НАПРАВЛЕНИЕ СТРЕЛКИ 
        arrow_size = 10

        perp_x = -uy
        perp_y = ux

        wing1 = canvas.Line(
            x1=end_x, y1=end_y,
            x2=end_x - ux*arrow_size + perp_x*arrow_size,
            y2=end_y - uy*arrow_size + perp_y*arrow_size,
            paint=flet.Paint(Colors.BLACK, stroke_width=2)
        )
        wing2 = canvas.Line(
            x1=end_x, y1=end_y,
            x2=end_x - ux*arrow_size - perp_x*arrow_size,
            y2=end_y - uy*arrow_size - perp_y*arrow_size,
            paint=flet.Paint(Colors.BLACK, stroke_width=2)
        )

        # ПОДПИСЬ СТРЕЛКИ
        label_x = (start_x + end_x) / 2 + 50
        label_y = (start_y + end_y) / 2 - 20
        label = canvas.Text(
            x=label_x,
            y=label_y,
            text=symbol,
            style=TextStyle(size=18, weight=FontWeight.BOLD),
        )


        drawing_area.shapes.extend([arrow_line, wing1, wing2, label])
        drawing_area.update()

    
    add_transition_button = ElevatedButton("Добавить переход")
    add_transition_button.on_click = add_transition

    gesture_area = GestureDetector(
        content=drawing_area,
        on_tap_down=add_node,
    )

    graph_area = Container(
        bgcolor=Colors.WHITE,
        width=700,
        height=450,
        border_radius=10,
        alignment=alignment.center,
        content=gesture_area,
    )

    instructions = Card(
        content=Container(
            content=Column(
                [
                    Text("Добавление переходов", size=18, weight="bold"),
                    start_state_input,
                    end_state_input,
                    symbol_input,
                    add_transition_button,
                ],
                spacing=15,
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.START,
            ),
            padding=20,
            bgcolor=Colors.WHITE,
            width=250,
            alignment=alignment.top_center,
        )
    )

    run_button = ElevatedButton("Обработать слово")

    page.add(
        Row(
            [
                Container(
                    content=Column(
                        [
                            Container(
                                content=Text(
                                    "Система обработки ДКА / НКА",
                                    size=24,
                                    weight="bold",
                                ),
                                margin=flet.margin.only(left=120),
                            ),
                            graph_area,
                            Container(
                                content=Row([word_input, run_button], spacing=20),
                                margin=flet.margin.only(top=11),
                            ),
                        ],
                        spacing=20,
                    ),
                    padding=20,
                ),
                Container(
                    content = instructions,
                    width = 400
                )
            ],
            spacing=30,
            alignment=MainAxisAlignment.START,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    flet.app(target=main)