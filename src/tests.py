# =====================================================================
# КАТЕГОРИЯ 1: ЧИСТАЯ МАТЕМАТИКА И АЛГОРИТМЫ
# Идеальные кандидаты для юнит-тестов. Не требуют вообще никаких моков,
# кроме встроенных или простых типов данных (строки, множества, числа).
# =====================================================================

# --- linal.py ---
# Вся линейная алгебра тестируется элементарно через assert.
class Vector2D:
    def length(self) -> float: pass
    def normalized(self) -> 'Vector2D': pass
    def turned(self, radians: float) -> 'Vector2D': pass
    def perpendicular(self) -> 'Vector2D': pass
    def phi(self) -> float: pass
    # Операторы: __add__, __sub__, __mul__, __truediv__

def dot_product(v1: Vector2D, v2: Vector2D) -> float: pass


# --- automata_operations.py ---
# Работа со строками (регулярными выражениями).
def _is_wrapped(regex: str) -> bool: pass
def _wrap_if_needed(regex: str) -> str: pass
def _union_regex(left: str | None, right: str | None) -> str | None: pass
def _concat_regex(*parts: str | None) -> str | None: pass
# Если в файле присутствует алгоритм исключения состояний:
def nfa_to_regex_state_elimination(nfa) -> str: pass 


# --- debug.py ---
# Чистый алгоритм обхода графа (поиск в глубину/ширину по ε-переходам).
def get_epsilon_closure(nfa, states: set) -> set: pass


# =====================================================================
# КАТЕГОРИЯ 2: КОНВЕРТАЦИЯ СТРУКТУР И РАБОТА С СОСТОЯНИЕМ
# Логика преобразования форматов данных (NFA <-> JSON <-> Graph).
# Требуются заглушки для классов-контейнеров (DFA/NFA из библиотеки).
# =====================================================================

# --- automata_io.py ---
# Проверка корректности сериализации/десериализации файлов.
def save_automaton_to_json(automaton, file_path: str, regex: str = "") -> None: pass
def load_automaton_from_json(file_path: str) -> tuple: pass


# --- automation_to_graph.py ---
# Проверка того, что узлы и ребра правильно перекладываются в библиотеку igraph.
def convert_automaton_to_igraph(attr) -> 'ig.Graph': pass


# --- graph.py ---
# Тестирование логики фильтрации внутри хранилища графа.
class Graph:
    def get_final_states(self) -> set: pass
    def get_start_states(self) -> set: pass


# --- graph_history.py ---
# Тестирование буфера кольцевой истории (добавление, сдвиг при max_count).
class History:
    def add(self, action: Graph) -> None: pass
    # Методы undo_click/redo_click тестировать сложнее из-за вызова draw_nodes(app)


# =====================================================================
# КАТЕГОРИЯ 3: ГЕОМЕТРИЯ КАНВАСА И РАСЧЕТЫ (Требуют Mock(App))
# Здесь нет прямых вызовов flet (отрисовки), но есть сложная геометрия.
# Для тестирования понадобится создать объект-пустышку app, содержащий 
# app.graph (с узлами) и app.config.
# =====================================================================

# --- canvas_utils.py ---
# Аналитическая геометрия: проекции точек, пересечения, радиусы.
def get_clicked_node(click: Vector2D, app: 'Application') -> 'Node': pass
def get_clicked_transition(click: Vector2D, app: 'Application') -> 'Transition': pass
def check_self_transition(click: Vector2D, transition: 'Transition', app: 'Application') -> bool: pass


# --- canvas_events.py ---
# Вспомогательные проверки координат.
def _is_inside_canvas(point: Vector2D, app: 'Application') -> bool: pass
def _event_point(e) -> Vector2D: pass # Проверка маппинга координат из события Flet


# --- edit_events.py ---
# Математическое масштабирование координат всех узлов графа.
def _scale_graph_positions(app: 'Application', old_scale: float, new_scale: float) -> None: pass


# --- draw.py ---
# Из модуля рисования можно тестировать чисто математические функции расчетов
# (если они вынесены из функций, напрямую генерирующих объекты ft.canvas).
def is_line_intersecting_node(start_p: Vector2D, end_p: Vector2D, app: 'Application') -> bool: pass