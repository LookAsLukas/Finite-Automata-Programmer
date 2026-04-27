from enum import Enum
from flet import Colors, Text, TextField, canvas, ElevatedButton, Container, Slider
from dataclasses import dataclass, field
from typing import Set

EPSILON_SYMBOL = "ε"


class EditorMode(Enum):
    SELECT = "select"
    NODES = "nodes"
    TRANSITIONS = "transitions"


@dataclass
class ApplicationState:
    editor_mode: EditorMode = EditorMode.SELECT
    alphabet: Set[str] = field(default_factory=set)
    regex: str = ""
    base_canvas_width: float = 700
    base_canvas_height: float = 450
    canvas_width: float = 700
    canvas_height: float = 450
    canvas_scale: float = 1.0
    min_canvas_scale: float = 0.5
    max_canvas_scale: float = 2.0
    canvas_scale_step: float = 0.1

    debug_mode: bool = False 
    current_states: Set[str] = field(default_factory=set) 
    input_string: str = ""
    input_position: int = 0 
    


@dataclass
class ApplicationUI:
    word_input = TextField(label="Слово для проверки", color=Colors.BLACK)
    alphabet_input = TextField(label="Добавить символ", hint_text="Символ...", width=150, color=Colors.BLACK)
    
    drawing_area = canvas.Canvas(width=700, height=450)

    status_text = Text("Готов к работе", size=14, color=Colors.BLUE_GREY_700)
    alphabet_display = Text("Алфавит: ∅", size=14, color=Colors.BLACK)
    regex_display = Text("Регулярное выражение: не задано", size=14, color=Colors.GREEN)
    
    open_file_picker = None
    save_file_picker = None

    debug_step_back_btn = ElevatedButton("Назад")
    debug_step_forward_btn = ElevatedButton("Вперед")
    debug_continue_btn = ElevatedButton("Продолжить")
    debug_status_text = Text("")
    debug_panel = Container(visible=False)

    canvas_container = None
    mode_select_button = None
    mode_nodes_button = None
    mode_transitions_button = None
    canvas_scale_text = Text("100%", size=14, color=Colors.BLACK)
    canvas_scale_slider = Slider(min=50, max=200, value=100, divisions=30)
