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
)


def main(page: Page):
    page.title = "FAP"
    page.window_width = 800
    page.window_height = 500
    page.bgcolor = Colors.BLUE_GREY_50

    nodes = []
    node_counter = 0

    word_input = TextField(
        label="Слово для обработки",
        hint_text="Введите слово...",
        width=535,
    )

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
            content=Text("Это карточка с инструкциями", size=18),
            padding=20,
            bgcolor=Colors.WHITE,
            width=450,
            height=600,
            alignment=alignment.center,
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
                instructions,
            ],
            spacing=30,
            alignment=MainAxisAlignment.START,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )
    )


flet.app(target=main)
