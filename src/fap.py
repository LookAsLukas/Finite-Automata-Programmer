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
    clear_automaton,
    handle_delete
)
from interaction_events import (
    handle_run,
    request_file_open,
    request_file_save,
    handle_open_file_result,
    handle_save_file_result,
)
from dialog_handlers import regex_input_dialog
from automaton_optimization import handle_optimize_click

def main(page: Page):
    page.title = "FAP — Визуальный конструктор НКА"
    page.padding = 0
    page.bgcolor = Colors.BLUE_GREY_50
    
    # Убираем ВСЕ фиксированные размеры и ограничения
    # Окно будет любого размера, какой задаст пользователь

    attr = ApplicationAttributes()
    ui = ApplicationUI()

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

    delete_button = ElevatedButton("Удалить", on_click=lambda e: handle_delete(e, attr, ui, page))
    place_mode_button = ElevatedButton("Режим добавления состояний", on_click=lambda e: toggle_placing_mode(e, attr, ui, page))
    transition_mode_button = ElevatedButton("Режим добавления переходов", on_click=lambda e: toggle_transition_mode(e, attr, ui, page))
    start_button = ElevatedButton("Переключить начальное состояние", on_click=lambda e: toggle_start_state(e, attr, ui, page))
    final_button = ElevatedButton("Переключить конечное состояние", on_click=lambda e: toggle_final_state(e, attr, ui, page))
    run_button = ElevatedButton("Обработать слово", on_click=lambda e: handle_run(e, attr, ui, page))
    add_alphabet_button = ElevatedButton("Добавить символ", on_click=lambda e: add_alphabet_symbol(e, attr, ui, page))
    clear_button = ElevatedButton("Очистить автомат", on_click=lambda e: clear_automaton(e, attr, ui, page))
    regex_button = ElevatedButton("Построить из регулярного выражения", on_click=lambda e: page.open(regex_input_dialog(attr, ui, page)))
    optimize_button = ElevatedButton("Оптимизировать (Min DFA)", on_click=lambda e: handle_optimize_click(e, attr, ui, page),bgcolor=Colors.GREEN_100, color=Colors.GREEN_900)

    # Канвас ФИКСИРОВАННОГО размера
    canvas_container = Container(
        width=700,  # Фиксированная ширина
        height=450,  # Фиксированная высота
        bgcolor=Colors.WHITE,
        border_radius=10,
        alignment=alignment.center,
    )
    
    canvas_container.content = ui.drawing_area
    
    gesture_area = GestureDetector(
        content=canvas_container,
        on_tap_down=lambda e: handle_canvas_click(e, attr, ui, page),
        on_double_tap_down=lambda e: handle_double_click(e, attr, ui, page),
        on_pan_start=lambda e: handle_drag_start(e, attr, ui, page),
        on_pan_update=lambda e: handle_drag_update(e, attr, ui, page),
        on_pan_end=lambda e: handle_drag_end(e, attr, ui, page)
    )

    # ---------- Компоновка ----------
    graph_area = Container(
        content=gesture_area,
        alignment=alignment.center,
    )

    # Делаем Row с полем ввода и кнопкой на всю доступную ширину
    input_row = Row(
        [
            Container(
                content=ui.word_input,
                expand=True,  # Занимает всё доступное пространство
            ),
            run_button,
        ],
        spacing=10,
        expand=True,  # Row тоже расширяется
        vertical_alignment=CrossAxisAlignment.CENTER,
    )

    page.add(
        Column(
            [
                Row(
                    [
                        # Левая часть с канвасом - занимает оставшееся пространство
                        Container(
                            expand=True,
                            content=Column(
                                [
                                    Text("Визуальный автомат (NFA)", size=24, weight="bold"),
                                    graph_area,
                                    Column([ui.mode_status, ui.transition_status, ui.status_text], spacing=5),
                                    Container(
                                        content=input_row,
                                        expand=True,  # Контейнер тоже расширяется
                                    ),
                                ],
                                spacing=15,
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                                expand=True,
                            ),
                            padding=20,
                            alignment=alignment.center,
                        ),
                        # Правая часть с кнопками - фиксированной ширины
                        Container(
                            padding=20,
                            width=450,  # Фиксированная ширина правой панели
                            content=Column(
                                [
                                    Card(content=Container(content=Column([Text("Режимы", size=18, weight="bold"), place_mode_button, transition_mode_button, delete_button], spacing=10, horizontal_alignment=CrossAxisAlignment.STRETCH), padding=10)),
                                    Card(content=Container(content=Column([Text("Алфавит", size=18, weight="bold"), Row([ui.alphabet_input, add_alphabet_button], spacing=10), ui.alphabet_display], spacing=10, horizontal_alignment=CrossAxisAlignment.STRETCH), padding=10)),
                                    Card(content=Container(content=Column([Text("Регулярные выражения", size=18, weight="bold"), ui.regex_display, regex_button], spacing=10, horizontal_alignment=CrossAxisAlignment.STRETCH), padding=10)),
                                    start_button, final_button, clear_button, optimize_button,
                                ],
                                spacing=20,
                                alignment=MainAxisAlignment.START,
                                horizontal_alignment=CrossAxisAlignment.STRETCH,
                            ),
                        ),
                    ],
                    spacing=5,
                    vertical_alignment=CrossAxisAlignment.START,
                    expand=True,
                ),
            ],
            spacing=10,
            expand=True,
        )
    )

    draw_nodes(attr, ui)
    page.update()

if __name__ == "__main__":
    flet.app(target=main)