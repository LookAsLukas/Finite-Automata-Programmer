# ==========================================
# ФАЙЛ: automata_io.py
# Чистая логика сохранения и загрузки данных, не зависящая от UI.
# ==========================================
def save_automaton_to_json(automaton, file_path: str, regex: str = ""):
    pass

def load_automaton_from_json(file_path: str): # Сигнатура восстановлена из контекста
    pass


# ==========================================
# ФАЙЛ: automata_operations.py
# Вспомогательные чистые функции для работы с регулярными выражениями.
# ==========================================
def _is_wrapped(regex: str) -> bool:
    pass

def _wrap_if_needed(regex: str) -> str:
    pass

def _union_regex(left: str | None, right: str | None) -> str | None:
    pass

def _concat_regex(*parts: str | None) -> str | None:
    pass


# ==========================================
# ФАЙЛ: automation_to_graph.py
# Изолированная функция конвертации состояния в формат igraph.
# ==========================================
def convert_automaton_to_igraph(attr):
    pass


# ==========================================
# ФАЙЛ: debug.py
# Алгоритм обхода графа, полностью независимый от Flet.
# ==========================================
def get_epsilon_closure(nfa, states) -> set:
    """Находит все состояния, достижимые из текущих по эпсилон-переходам."""
    pass


# ==========================================
# ФАЙЛ: graph.py
# Методы класса Graph, которые возвращают отфильтрованные данные (чистая логика).
# ==========================================
class Graph:
    def get_final_states(self) -> set:
        pass

    def get_start_states(self) -> set:
        pass


# ==========================================
# ФАЙЛ: linal.py
# Вся линейная алгебра - это идеальный кандидат для TDD (разработки через тестирование).
# ==========================================
class Vector2D:
    @staticmethod
    def from_node(node): pass
    
    @staticmethod
    def from_transition(transition): pass
    
    @staticmethod
    def from_phi_r(phi, r): pass
    
    def to_tuple(self): pass
    
    def phi(self): pass
    
    def length(self): pass
    
    def normalized(self): pass
    
    def turned(self, radians): pass
    
    def perpendicular(self): pass
    
    # Плюс можно протестировать перегруженные операторы:
    # __add__, __sub__, __mul__, __truediv__


# ==========================================
# ФАЙЛ: canvas_utils.py
# Математическая и геометрическая логика пересечений и кликов. 
# Зависит от объекта app, но его можно легко замокать, передав болванку Graph.
# ==========================================
def get_clicked_node(click, app):
    pass

def check_self_transition(click, transition, app) -> bool:
    pass


# ==========================================
# ФАЙЛ: graph_history.py
# Логика стека истории (отделена от визуализации, кроме методов undo/redo).
# ==========================================
class History:
    def add(self, action):
        """Тестируем правильное добавление в буфер и обрезку по max_count."""
        pass