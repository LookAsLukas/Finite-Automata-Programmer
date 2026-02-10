from flet import Colors, Text, TextField, canvas, ElevatedButton, Container
from dataclasses import dataclass, field
from typing import Set

EPSILON_SYMBOL = "ε"


@dataclass
class ApplicationState:
    placing_mode: bool = False
    transition_mode: bool = False
    alphabet: Set[str] = field(default_factory=set)
    regex = ""
    canvas_width = 700
    canvas_height = 450

    debug_mode: bool = False 
    current_states: Set[str] = field(default_factory=set) 
    input_string: str = ""
    input_position: int = 0 
    


@dataclass
class ApplicationUI:
    word_input = TextField(label="Слово для проверки")
    alphabet_input = TextField(label="Добавить символ", hint_text="Символ...", width=150)
    
    drawing_area = canvas.Canvas(width=700, height=450)

    mode_status = Text("Режим размещения: выключен", size=16, color=Colors.GREY_800)
    status_text = Text("Готов к работе", size=14, color=Colors.BLUE_GREY_700)
    alphabet_display = Text("Алфавит: ∅", size=14)
    regex_display = Text("Регулярное выражение: не задано", size=14, color=Colors.GREEN)
    
    open_file_picker = None
    save_file_picker = None

    debug_step_back_btn = ElevatedButton("Назад") 
    debug_step_forward_btn = ElevatedButton("Вперед")
    debug_continue_btn = ElevatedButton("Продолжить")
    debug_status_text = Text("")
    debug_panel = Container(visible=False)