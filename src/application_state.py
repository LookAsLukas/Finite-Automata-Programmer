from flet import Colors, Text, TextField, canvas, Row, Column, Container, MainAxisAlignment, ScrollMode
from dataclasses import dataclass, field


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
    # UI элементы
    
    # 1. Убрали width=400, чтобы поле могло растягиваться. 
    # В интерфейсе его лучше поместить в Row с expand=True
    word_input = TextField(label="Слово для проверки")
    
    # 2. width=150 можно оставить для маленького поля, или тоже убрать
    alphabet_input = TextField(label="Добавить символ", hint_text="Символ...", width=150)
    
    # Фиксированный размер канваса (как и требовалось)
    drawing_area = canvas.Canvas(width=700, height=450)
    
    # Статусы и тексты
    mode_status = Text("Режим размещения: выключен", size=16, color=Colors.GREY_800)
    transition_status = Text("Режим переходов: выключен", size=16, color=Colors.GREY_800)
    status_text = Text("Добавьте состояния или переходы", size=16, color=Colors.GREY_800)
    alphabet_display = Text("Алфавит: ∅", size=16, color=Colors.BLUE_800)
    
    open_file_picker = None
    save_file_picker = None
    regex_display = Text("Регулярное выражение: не задано", size=16, color=Colors.GREEN_800)