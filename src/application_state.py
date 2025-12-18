from flet import Colors, Text, TextField, canvas
from dataclasses import dataclass

EPSILON_SYMBOL = "ε"

@dataclass
class ApplicationAttributes:
    # Константы размеров канваса
    CANVAS_WIDTH = 700
    CANVAS_HEIGHT = 450
    
    # nodes: {state_name: (x, y)}
    nodes = {}
    node_counter = 0
    start_state = None
    final_states = set()
    transitions = {}  # {start_state: [{"symbol": "a", "end": "q1"}]}
    selected_node = None
    first_selected_node = None
    placing_mode = False
    transition_mode = False
    alphabet = set()
    dragging_node = None  
    selected_transition = None
    regex = ""
    canvas_width = CANVAS_WIDTH
    canvas_height = CANVAS_HEIGHT


@dataclass
class ApplicationUI:
    word_input = TextField(label="Слово для проверки")
    alphabet_input = TextField(label="Добавить символ", hint_text="Символ...", width=150)
    
    drawing_area = canvas.Canvas(width=700, height=450)

    mode_status = Text("Режим размещения: выключен", size=16, color=Colors.GREY_800)
    transition_status = Text("Режим переходов: выключен", size=16, color=Colors.GREY_800)
    status_text = Text("Готов к работе", size=14, color=Colors.BLUE_GREY_700)
    alphabet_display = Text("Алфавит: ∅", size=14)
    regex_display = Text("Регулярное выражение: не задано", size=14, color=Colors.BLACK54)
    
    open_file_picker = None
    save_file_picker = None