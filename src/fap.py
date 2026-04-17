import flet as ft
from flet import (
    Text,
    AppBar,
    ElevatedButton,
    Column,
    Row,
    Container,
    Colors,
    alignment,
    CrossAxisAlignment,
    MainAxisAlignment,
    GestureDetector,
    PopupMenuButton,
    PopupMenuItem,
    FilePicker,
    Slider,
    IconButton,
)

from application_state import ApplicationUI, ApplicationState
from graph import Graph
from config import ApplicatonConfig
from graph_history import History
from draw import Draw
from table import open_table_editor
import debug


class Application:
    graph = Graph()
    attr = ApplicationState()
    ui = ApplicationUI()
    config = ApplicatonConfig()
    history = History()
    page: ft.Page

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "FAP — Визуальный конструктор НКА"
        self.page.padding = 0
        self.page.bgcolor = Colors.BLUE_GREY_50
        self.page.add(self.build_page())
        self.draw = Draw(self)
        self.page.update()

    def copy_regex(self, e):
        if self.attr.regex:
            self.page.set_clipboard(self.attr.regex)
            self.ui.status_text.value = "Регулярное выражение скопировано"
        else:
            self.ui.status_text.value = "Нет регулярного выражения для копирования"
        self.page.update()

    def build_page(self):
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

        self.ui.debug_step_back_btn = ElevatedButton(
            "← Шаг назад",
            on_click=lambda e: debug.debug_step_back(self),
            bgcolor=Colors.AMBER_100
        )
        self.ui.debug_step_forward_btn = ElevatedButton(
            "Шаг вперед →",
            on_click=lambda e: debug.debug_step_forward(self),
            bgcolor=Colors.GREEN_100
        )
        self.ui.debug_continue_btn = ElevatedButton(
            "Продолжить",
            on_click=lambda e: debug.debug_continue(self),
            bgcolor=Colors.BLUE_100
        )
        self.ui.debug_status_text = Text(
            "",
            size=12,
            color=Colors.BLUE_700,
            weight="bold",
            visible=False
        )

        # ТОЛЬКО ПОТОМ создаем debug_panel
        self.ui.debug_panel = Container(
            content=Row([
                self.ui.debug_step_back_btn,
                self.ui.debug_step_forward_btn,
                self.ui.debug_continue_btn
            ], spacing=10),
            padding=10,
            bgcolor=Colors.GREY_200,
            border_radius=5,
            visible=False  # Изначально скрыт
        )

        self.page.appbar = AppBar(
            bgcolor=Colors.BLUE_GREY_900,
            toolbar_height=48,
            title=Row([
                PopupMenuButton(
                    content=Text("Файл", color=Colors.WHITE, weight="bold"),
                    items=[
                        PopupMenuItem(text="Открыть файл", on_click=lambda e: request_file_open(self)),
                        PopupMenuItem(text="Сохранить файл", on_click=lambda e: request_file_save(self)),
                    ],),
                ElevatedButton(
                    "Undo",
                    on_click=lambda e: self.history.undo_click(self)
                ),
                ElevatedButton(
                    "Redo",
                    on_click=lambda e: self.history.redo_click(self)
                )]),
            center_title=False,
            actions=[
                self.ui.debug_panel,  # Теперь точно не None
                ElevatedButton(
                    "Отладка",
                    on_click=lambda e: debug.toggle_debug_mode(self),
                    bgcolor=Colors.YELLOW_100
                )
            ],
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
        self.ui.drawing_area.width = self.attr.canvas_width
        self.ui.drawing_area.height = self.attr.canvas_height

        canvas_container = Container(
            content=self.ui.drawing_area,
            width=self.attr.canvas_width,
            height=self.attr.canvas_height,
            bgcolor=Colors.WHITE,
            border_radius=10,
            alignment=alignment.center,
        )
        self.ui.canvas_container = canvas_container

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
                expand=True,
            ),
            ElevatedButton("Обработать слово", on_click=lambda e: interaction_events.handle_run(self))],
            spacing=10,
            vertical_alignment=CrossAxisAlignment.CENTER,
        )

        top_content = Column([
            Text("Визуальный автомат (NFA)", size=24, weight="bold", color=Colors.BLACK),
            Container(
                content=gesture_area,
                alignment=alignment.center,
            ),
            Column([
                self.ui.mode_status,
                self.ui.status_text],
                spacing=5
            )],
            spacing=15,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )

        return Container(
            expand=True,
            content=Column([
                Container(
                    content=top_content,
                    alignment=alignment.top_center,
                ),
                Container(expand=True),
                input_row],
                spacing=0,
                horizontal_alignment=CrossAxisAlignment.STRETCH,
                expand=True,
            ),
            padding=20,
        )

    def build_control_side(self):
        import edit_events
        import dialog_handlers
        import automaton_optimization
        import interaction_events

        def build_sidebar_section(title, controls, show_divider=True):
            content_controls = []
            if title:
                content_controls.append(Text(title, size=18, weight="bold", color=Colors.BLACK))
            content_controls.extend(controls)

            return Container(
                content=Column(
                    content_controls,
                    spacing=10,
                    horizontal_alignment=CrossAxisAlignment.STRETCH,
                ),
                padding=16,
                border=ft.border.only(
                    bottom=ft.border.BorderSide(1, Colors.BLUE_GREY_100)
                ) if show_divider else None,
            )

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
            "Добавить",
            on_click=lambda e: edit_events.add_alphabet_symbols(self)
        )
        remove_alphabet_button = ElevatedButton(
            "Удалить",
            on_click=lambda e: edit_events.remove_alphabet_symbols(self)
        )
        clear_button = ElevatedButton(
            "Очистить автомат",
            on_click=lambda e: edit_events.clear_automaton(self)
        )
        regex_button = ElevatedButton(
            "Построить из регулярного выражения",
            on_click=lambda e: self.page.open(dialog_handlers.regex_input_dialog(self))
        )
        regex_from_automaton_button = ElevatedButton(
            "Преобразовать в регулярное выражение",
            on_click=lambda e: interaction_events.handle_convert_to_regex(self)
        )
        optimize_button = ElevatedButton(
            "Оптимизировать (Min DFA)",
            on_click=lambda e: automaton_optimization.handle_optimize_click(self),
            bgcolor=Colors.GREEN_100,
            color=Colors.GREEN_900
        )
        table_editor_button = ElevatedButton(
            "Редактор таблицы",
            on_click=lambda e: open_table_editor(self)
        )
        zoom_out_button = ElevatedButton(
            "-",
            on_click=lambda e: edit_events.zoom_canvas_out(self),
            width=44
        )
        zoom_in_button = ElevatedButton(
            "+",
            on_click=lambda e: edit_events.zoom_canvas_in(self),
            width=44
        )
        self.ui.canvas_scale_slider = Slider(
            min=self.attr.min_canvas_scale * 100,
            max=self.attr.max_canvas_scale * 100,
            value=self.attr.canvas_scale * 100,
            divisions=int((self.attr.max_canvas_scale - self.attr.min_canvas_scale) / self.attr.canvas_scale_step),
            on_change=lambda e: edit_events.set_canvas_scale_from_slider(e, self),
            expand=True
        )
        self.ui.canvas_scale_text.value = f"{int(self.attr.canvas_scale * 100)}%"

        return Container(
            content=Column([
                build_sidebar_section("Режимы", [
                    place_mode_button,
                    transition_mode_button,
                    delete_button,
                ]),
                build_sidebar_section("Редактор", [
                    table_editor_button,
                ]),
                build_sidebar_section("Алфавит", [
                    Row([self.ui.alphabet_input, add_alphabet_button, remove_alphabet_button], spacing=10),
                    self.ui.alphabet_display,
                ]),
                build_sidebar_section("Регулярные выражения", [
                    Row([
                        self.ui.regex_display,
                        IconButton(
                            icon=ft.Icons.COPY,
                            tooltip="Копировать выражение",
                            on_click=self.copy_regex,
                        ),
                    ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                    regex_button,
                    regex_from_automaton_button,
                ]),
                build_sidebar_section("Масштаб поля", [
                    Row([zoom_out_button, self.ui.canvas_scale_slider, zoom_in_button, self.ui.canvas_scale_text], spacing=8),
                ]),
                build_sidebar_section(None, [
                    start_button,
                    final_button,
                    clear_button,
                    optimize_button,
                ], show_divider=False),
            ],
                spacing=0,
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.STRETCH,
            ),
            bgcolor=Colors.WHITE,
            padding=ft.padding.only(top=20, bottom=20),
            width=450,
        )


if __name__ == "__main__":
    ft.app(target=lambda page: Application(page))
