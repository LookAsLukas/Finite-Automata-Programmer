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
    MainAxisAlignment
)

def main(page: Page):
    page.title = "FAP"
    page.window_width = 800
    page.window_height = 500
    page.bgcolor = Colors.BLUE_GREY_50

    #ввод слова
    word_input = TextField(
        label="Слово для обработки",
        hint_text="Введите слово...",
        width=535,
    )

    graph_area = Container(
        bgcolor=Colors.WHITE,
        width=700,
        height=450,
        border_radius=10,
        alignment=alignment.center,
        content=Text("Здесь будет графическое построение автомата", color=Colors.GREY),
    )

    instructions = Card(
            content=Container(
                content=Text("Это карточка с инструкциями", size=18),
                padding=20,
                bgcolor=Colors.WHITE,
                width=450,
                height=600,
                alignment=alignment.center
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
                                    content=Text("Система обработки ДКА / НКА", size=24, weight="bold"),
                                    margin=flet.margin.only(left=120) 
                                ),
                                Container(content=graph_area),
                                Container(
                                    content=Row([word_input, run_button], spacing=20),
                                    margin=flet.margin.only(top=11) 
                                )
                            ],
                            spacing=20,
                        ),
                        padding=20  
                    ),
                    instructions
                ],
                spacing=30,
                alignment=MainAxisAlignment.START,
                vertical_alignment=CrossAxisAlignment.CENTER  
            )
        )

flet.app(target=main)

