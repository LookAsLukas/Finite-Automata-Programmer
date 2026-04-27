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
        self.apply_theme()
        import draw
        draw.draw_nodes(self)
        self.page.update()

    def theme_colors(self):
        if self.config.theme == "dark":
            return {
                "page": Colors.BLUE_GREY_900,
                "surface": Colors.BLUE_GREY_800,
                "canvas": Colors.BLUE_GREY_700,
                "mode": Colors.BLUE_GREY_900,
                "text": Colors.WHITE,
                "muted": Colors.BLUE_GREY_100,
                "regex": Colors.GREEN_200,
            }
        return {
            "page": Colors.BLUE_GREY_50,
            "surface": Colors.WHITE,
            "canvas": Colors.WHITE,
            "mode": Colors.BLUE_GREY_50,
            "text": Colors.BLACK,
            "muted": Colors.BLUE_GREY_700,
            "regex": Colors.GREEN,
        }

    def apply_theme(self):
        colors = self.theme_colors()
        self.page.theme_mode = ft.ThemeMode.DARK if self.config.theme == "dark" else ft.ThemeMode.LIGHT
        self.page.bgcolor = colors["page"]
        self.ui.word_input.color = colors["text"]
        self.ui.alphabet_input.color = colors["text"]
        self.ui.status_text.color = colors["muted"]
        self.ui.alphabet_display.color = colors["text"]
        self.ui.regex_display.color = colors["regex"]
        self.ui.canvas_scale_text.color = colors["text"]
        if self.ui.canvas_title is not None:
            self.ui.canvas_title.color = colors["text"]
        if self.ui.canvas_container is not None:
            self.ui.canvas_container.bgcolor = colors["canvas"]
        if self.ui.control_side is not None:
            self.ui.control_side.bgcolor = colors["surface"]
        if self.ui.mode_selector is not None:
            self.ui.mode_selector.bgcolor = colors["mode"]
        for text in self.ui.theme_texts:
            text.color = colors["text"]

    def build_settings_dialog(self):
        import draw

        node_size_text = Text(f"{self.config.node_text_size}px")
        transition_size_text = Text(f"{self.config.transition_text_size}px")

        def on_theme_change(e):
            self.config.theme = e.control.value
            self.apply_theme()
            draw.draw_nodes(self)
            self.page.update()

        def on_node_size(e):
            self.config.node_text_size = int(e.control.value)
            node_size_text.value = f"{self.config.node_text_size}px"
            draw.draw_nodes(self)
            self.page.update()

        def on_transition_size(e):
            self.config.transition_text_size = int(e.control.value)
            transition_size_text.value = f"{self.config.transition_text_size}px"
            draw.draw_nodes(self)
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=Text("Настройки"),
            content=Container(
                width=360,
                content=Column([
                    Text("Внешний вид", size=16, weight="bold"),
                    ft.RadioGroup(
                        value=self.config.theme,
                        content=Row([
                            ft.Radio(value="light", label="Светлая"),
                            ft.Radio(value="dark", label="Темная"),
                        ]),
                        on_change=on_theme_change,
                    ),
                    Text("Размер имени нод"),
                    Row([
                        Slider(min=10, max=28, divisions=18, value=self.config.node_text_size, on_change=on_node_size, expand=True),
                        node_size_text,
                    ]),
                    Text("Размер символов перехода"),
                    Row([
                        Slider(min=10, max=32, divisions=22, value=self.config.transition_text_size, on_change=on_transition_size, expand=True),
                        transition_size_text,
                    ]),
                ], tight=True),
            ),
            actions=[ElevatedButton("Закрыть", on_click=lambda e: self.page.close(dialog))],
        )
        return dialog

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
        self.ui.theme_texts = []
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
                IconButton(
                    icon=ft.Icons.SETTINGS,
                    tooltip="Настройки",
                    icon_color=Colors.WHITE,
                    on_click=lambda e: self.page.open(self.build_settings_dialog()),
                ),
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

        self.ui.canvas_title = Text("Визуальный автомат (NFA)", size=24, weight="bold", color=self.theme_colors()["text"])

        top_content = Column([
            self.ui.canvas_title,
            Container(
                content=gesture_area,
                alignment=alignment.center,
            ),
            self.ui.status_text],
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
                title_text = Text(title, size=18, weight="bold", color=self.theme_colors()["text"])
                self.ui.theme_texts.append(title_text)
                content_controls.append(title_text)
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
        self.ui.mode_select_button = ElevatedButton(
            "Выбор",
            icon=ft.Icons.PAN_TOOL,
            tooltip="Обычный режим: выбор, редактирование и перетаскивание",
            on_click=lambda e: edit_events.activate_selection_mode(self),
            expand=True,
            height=52,
        )
        self.ui.mode_nodes_button = ElevatedButton(
            "Состояния",
            icon=ft.Icons.TOUCH_APP,
            tooltip="Добавление новых состояний по клику на поле",
            on_click=lambda e: edit_events.activate_node_creation_mode(self),
            expand=True,
            height=52,
        )
        self.ui.mode_transitions_button = ElevatedButton(
            "Переходы",
            icon=ft.Icons.SWAP_HORIZ,
            tooltip="Добавление переходов между выбранными состояниями",
            on_click=lambda e: edit_events.activate_transition_creation_mode(self),
            expand=True,
            height=52,
        )
        edit_events.refresh_mode_buttons(self)
        self.ui.mode_selector = Container(
            content=Row(
                [
                    self.ui.mode_select_button,
                    self.ui.mode_nodes_button,
                    self.ui.mode_transitions_button,
                ],
                spacing=8,
            ),
            padding=4,
            bgcolor=Colors.BLUE_GREY_50,
            border_radius=18,
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

        self.ui.control_side = Container(
            content=Column([
                build_sidebar_section("Режимы", [
                    self.ui.mode_selector,
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
        return self.ui.control_side


if __name__ == "__main__":
    ft.app(target=lambda page: Application(page))
