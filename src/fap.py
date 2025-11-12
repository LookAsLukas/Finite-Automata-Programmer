import flet
from flet import (
    Page,
    Text,
    ElevatedButton,
    Column,
    Row,
    Container,
    Colors,
    alignment,
    CrossAxisAlignment,
    Card,
    MainAxisAlignment,
    GestureDetector,
)
from draw import draw_nodes
from application_state import ApplicationUI, ApplicationAttributes
from canvas_events import handle_canvas_click, handle_double_click
from edit_events import (
    toggle_final_state,
    toggle_placing_mode,
    toggle_start_state,
    toggle_transition_mode,
    add_alphabet_symbol,
    clear_automaton
)
from interaction_events import handle_run, export_nfa, import_automaton


def main(page: Page):
    page.title = "FAP — Визуальный конструктор НКА"
    page.window_width = 900
    page.window_height = 600
    page.bgcolor = Colors.BLUE_GREY_50

    attr = ApplicationAttributes()
    ui = ApplicationUI()

    # Кнопки
    place_mode_button = ElevatedButton("Режим добавления состояний", on_click=lambda e: toggle_placing_mode(e, attr, ui, page))
    transition_mode_button = ElevatedButton("Режим добавления переходов", on_click=lambda e: toggle_transition_mode(e, attr, ui, page))
    start_button = ElevatedButton("Переключить начальное состояние", on_click=lambda e: toggle_start_state(e, attr, ui, page))
    final_button = ElevatedButton("Переключить конечное состояние", on_click=lambda e: toggle_final_state(e, attr, ui, page))
    run_button = ElevatedButton("Обработать слово", on_click=lambda e: handle_run(e, attr, ui, page))
    export_button = ElevatedButton("Экспортировать NFA", on_click=lambda e: export_nfa(e, attr, ui, page))
    import_button = ElevatedButton("Импортировать автомат", on_click=lambda e: import_automaton(e, attr, ui, page))
    add_alphabet_button = ElevatedButton("Добавить символ", on_click=lambda e: add_alphabet_symbol(e, attr, ui, page))
    clear_button = ElevatedButton("Очистить автомат", on_click=lambda e: clear_automaton(e, attr, ui, page))

    gesture_area = GestureDetector(
        content=ui.drawing_area,
        on_tap_down=lambda e: handle_canvas_click(e, attr, ui, page),
        on_double_tap_down=lambda e: handle_double_click(e, attr, ui, page)
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
                            Column([ui.mode_status, ui.transition_status, ui.status_text], spacing=5),
                            Row([ui.word_input, run_button, export_button, import_button], spacing=10),
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
                                         Row([ui.alphabet_input, add_alphabet_button], spacing=10),
                                         ui.alphabet_display],
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

    draw_nodes(attr, ui)
    page.update()


if __name__ == "__main__":
    flet.app(target=main)
