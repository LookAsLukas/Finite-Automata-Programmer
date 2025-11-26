import flet
from flet import (
    Page,
    Text,
    AppBar,
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
    PopupMenuButton,
    PopupMenuItem,
    FilePicker,
)
from draw import draw_nodes
from application_state import ApplicationUI, ApplicationAttributes
from canvas_events import handle_drag_start, handle_drag_update, handle_drag_end
from canvas_events import handle_canvas_click, handle_double_click
from edit_events import (
    toggle_final_state,
    toggle_placing_mode,
    toggle_start_state,
    toggle_transition_mode,
    add_alphabet_symbol,
    clear_automaton
)
from interaction_events import (
    handle_run,
    request_file_open,
    request_file_save,
    handle_open_file_result,
    handle_save_file_result,
)
from dialog_handlers import regex_input_dialog

def main(page: Page):
    page.title = "FAP — Визуальный конструктор НКА"
    page.window_width = 900
    page.window_height = 600
    page.padding = 0
    page.bgcolor = Colors.BLUE_GREY_50

    attr = ApplicationAttributes()
    ui = ApplicationUI()

    # Диалоги выбора файла для импорта/экспорта
    ui.open_file_picker = FilePicker(on_result=lambda e: handle_open_file_result(e, attr, ui, page))
    ui.save_file_picker = FilePicker(on_result=lambda e: handle_save_file_result(e, attr, ui, page))
    page.overlay.append(ui.open_file_picker)
    page.overlay.append(ui.save_file_picker)

    page.appbar = AppBar(
        bgcolor=Colors.BLUE_GREY_900,
        toolbar_height=48,
        title=PopupMenuButton(
            content=Text("Файл", color=Colors.WHITE, weight="bold"),
            items=[
                PopupMenuItem(text="Открыть файл", on_click=lambda e: request_file_open(e, attr, ui, page)),
                PopupMenuItem(text="Сохранить файл", on_click=lambda e: request_file_save(e, attr, ui, page)),
            ],
        ),
        center_title=False,
        actions=[],
    )

    # Кнопки
    place_mode_button = ElevatedButton("Режим добавления состояний", on_click=lambda e: toggle_placing_mode(e, attr, ui, page))
    transition_mode_button = ElevatedButton("Режим добавления переходов", on_click=lambda e: toggle_transition_mode(e, attr, ui, page))
    start_button = ElevatedButton("Переключить начальное состояние", on_click=lambda e: toggle_start_state(e, attr, ui, page))
    final_button = ElevatedButton("Переключить конечное состояние", on_click=lambda e: toggle_final_state(e, attr, ui, page))
    run_button = ElevatedButton("Обработать слово", on_click=lambda e: handle_run(e, attr, ui, page))
    add_alphabet_button = ElevatedButton("Добавить символ", on_click=lambda e: add_alphabet_symbol(e, attr, ui, page))
    clear_button = ElevatedButton("Очистить автомат", on_click=lambda e: clear_automaton(e, attr, ui, page))
    regex_button = ElevatedButton("Построить из регулярного выражения", on_click=lambda e: page.open(regex_input_dialog(attr, ui, page)))

    gesture_area = GestureDetector(
    content=ui.drawing_area,
    on_tap_down=lambda e: handle_canvas_click(e, attr, ui, page),
    on_double_tap_down=lambda e: handle_double_click(e, attr, ui, page),
    on_pan_start=lambda e: handle_drag_start(e, attr, ui, page),
    on_pan_update=lambda e: handle_drag_update(e, attr, ui, page),
    on_pan_end=lambda e: handle_drag_end(e, attr, ui, page)
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
        Column(
            [
                Row(
                    [
                        Container(
                            content=Column(
                                [
                                    Text("Визуальный автомат (NFA)", size=24, weight="bold"),
                                    graph_area,
                                    Column([
                                        ui.mode_status, 
                                        ui.transition_status, 
                                        ui.status_text,
                                        ui.regex_display
                                    ], spacing=5),
                                    Row([ui.word_input, run_button], spacing=10),
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
                                    Card(
                                        content=Container(
                                            content=Column(
                                                [Text("Конструктор", size=18, weight="bold"),
                                                 regex_button],
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
                ),
            ],
            spacing=10,
        )
    )

    draw_nodes(attr, ui)
    page.update()


if __name__ == "__main__":
    flet.app(target=main)