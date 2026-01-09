import flet as ft
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

from application_state import ApplicationUI, ApplicationState
from graph import Graph
from config import ApplicatonConfig


class Application:
    graph = Graph()
    attr = ApplicationState()
    ui = ApplicationUI()
    config = ApplicatonConfig()
    page: ft.Page

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "FAP — Визуальный конструктор НКА"
        self.page.padding = 0
        self.page.bgcolor = Colors.BLUE_GREY_50
        self.page.add(self.build_page())
        import draw
        draw.draw_nodes(self)
        self.page.update()

    def build_page(self):
        # this particular module refuses to work if I import it without 'from'
        from interaction_events import (
            handle_open_file_result,
            handle_save_file_result,
            request_file_open,
            request_file_save
        )
        self.ui.open_file_picker = FilePicker(on_result=lambda e: handle_open_file_result(e, self))
        self.ui.save_file_picker = FilePicker(on_result=lambda e: handle_save_file_result(e, self))
        self.page.overlay.append(self.ui.open_file_picker)
        self.page.overlay.append(self.ui.save_file_picker)

        self.page.appbar = AppBar(
            bgcolor=Colors.BLUE_GREY_900,
            toolbar_height=48,
            title=PopupMenuButton(
                content=Text("Файл", color=Colors.WHITE, weight="bold"),
                items=[
                    PopupMenuItem(text="Открыть файл", on_click=lambda e: request_file_open(self)),
                    PopupMenuItem(text="Сохранить файл", on_click=lambda e: request_file_save(self)),
                ],
            ),
            center_title=False,
            actions=[],
        )

        return Column([
            Row(
                [self.build_canvas_side(), self.build_control_side()],
                spacing=5,
                vertical_alignment=CrossAxisAlignment.START,
                expand=True,
            )],
            spacing=10,
            expand=True,
        )

    def build_canvas_side(self):
        import canvas_events
        import interaction_events
        canvas_container = Container(
            content=self.ui.drawing_area,
            width=700,  # Фиксированная ширина
            height=450,  # Фиксированная высота
            bgcolor=Colors.WHITE,
            border_radius=10,
            alignment=alignment.center,
        )

        gesture_area = GestureDetector(
            content=canvas_container,
            on_tap_down=lambda e: canvas_events.handle_canvas_click(e, self),
            on_double_tap_down=lambda e: canvas_events.handle_double_click(e, self),
            on_pan_start=lambda e: canvas_events.handle_drag_start(e, self),
            on_pan_update=lambda e: canvas_events.handle_drag_update(e, self),
            on_pan_end=lambda e: canvas_events.handle_drag_end(e, self)
        )

        input_row = Row([
            Container(
                content=self.ui.word_input,
                expand=True,  # Занимает всё доступное пространство
            ),
            ElevatedButton("Обработать слово", on_click=lambda e: interaction_events.handle_run(self))],
            spacing=10,
            expand=True,  # Row тоже расширяется
            vertical_alignment=CrossAxisAlignment.CENTER,
        )

        return Container(
            expand=True,
            content=Column([
                Text("Визуальный автомат (NFA)", size=24, weight="bold"),
                Container(
                    content=gesture_area,
                    alignment=alignment.center,
                ),
                Column([
                    self.ui.mode_status,
                    self.ui.status_text],
                    spacing=5
                ),
                Container(
                    content=input_row,
                    expand=True,  # Контейнер тоже расширяется
                )],
                spacing=15,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                expand=True,
            ),
            padding=20,
            alignment=alignment.center,
        )

    def build_control_side(self):
        import edit_events
        import dialog_handlers
        import automaton_optimization
        delete_button = ElevatedButton(
            "Удалить",
            on_click=lambda e: edit_events.handle_delete(self)
        )
        place_mode_button = ElevatedButton(
            "Режим добавления состояний",
            on_click=lambda e: edit_events.toggle_placing_mode(self)
        )
        transition_mode_button = ElevatedButton(
            "Режим добавления переходов",
            on_click=lambda e: edit_events.toggle_transition_mode(self)
        )
        start_button = ElevatedButton(
            "Переключить начальное состояние",
            on_click=lambda e: edit_events.toggle_start_state(self)
        )
        final_button = ElevatedButton(
            "Переключить конечное состояние",
            on_click=lambda e: edit_events.toggle_final_state(self)
        )
        add_alphabet_button = ElevatedButton(
            "Добавить символ",
            on_click=lambda e: edit_events.add_alphabet_symbols(self)
        )
        clear_button = ElevatedButton(
            "Очистить автомат",
            on_click=lambda e: edit_events.clear_automaton(self)
        )
        regex_button = ElevatedButton(
            "Построить из регулярного выражения",
            on_click=lambda e: self.page.open(dialog_handlers.regex_input_dialog(self))
        )
        optimize_button = ElevatedButton(
            "Оптимизировать (Min DFA)",
            on_click=lambda e: automaton_optimization.handle_optimize_click(self),
            bgcolor=Colors.GREEN_100,
            color=Colors.GREEN_900
        )

        return Container(
            content=Column([
                Card(
                    Container(Column([
                        Text("Режимы", size=18, weight="bold"),
                        place_mode_button,
                        transition_mode_button,
                        delete_button],
                        spacing=10,
                        horizontal_alignment=CrossAxisAlignment.STRETCH,
                    ), padding=10)
                ),
                Card(
                    Container(Column([
                        Text("Алфавит", size=18, weight="bold"),
                        Row([self.ui.alphabet_input, add_alphabet_button], spacing=10),
                        self.ui.alphabet_display],
                        spacing=10,
                        horizontal_alignment=CrossAxisAlignment.STRETCH,
                    ), padding=10)
                ),
                Card(
                    Container(Column([
                        Text("Регулярные выражения", size=18, weight="bold"),
                        self.ui.regex_display,
                        regex_button],
                        spacing=10,
                        horizontal_alignment=CrossAxisAlignment.STRETCH,
                    ), padding=10)
                ),
                start_button,
                final_button,
                clear_button,
                optimize_button],
                spacing=20,
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.STRETCH,
            ),
            padding=20,
            width=450,  # Фиксированная ширина правой панели
        )


if __name__ == "__main__":
    ft.app(target=lambda page: Application(page))
