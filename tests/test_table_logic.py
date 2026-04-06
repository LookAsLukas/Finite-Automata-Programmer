import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Добавляем пути, чтобы импорты работали
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from table import TableEditor
from graph import Graph, Node
from application_state import ApplicationState, ApplicationUI

class TestTableLogic(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.graph = Graph()
        self.app.attr = ApplicationState()
        self.app.ui = ApplicationUI()
        self.app.page = MagicMock()
        self.app.history = MagicMock()

        # Создаем начальные узлы
        self.node_q0 = Node(x=10, y=10, name="q0")
        self.node_q1 = Node(x=20, y=20, name="q1")
        self.app.graph.nodes = {self.node_q0, self.node_q1}
        self.app.attr.alphabet = {'a'}

        # Инициализируем редактор
        self.editor = TableEditor(self.app)

    @patch('draw.draw_nodes')
    def test_apply_valid_changes(self, mock_draw):
        # Строим UI, чтобы заполнились cell_fields
        self.editor.build_table_ui()
        
        # Находим поле ввода для q0 по символу 'a'
        # В классе TableEditor поля хранятся в словаре cell_fields по ключу (state, symbol)
        input_field = self.editor.cell_fields.get(("q0", "a"))
        self.assertIsNotNone(input_field)
        
        # Имитируем ввод пользователя: переход из q0 в q1 по 'a'
        input_field.value = "q1"

        # Кликаем "Применить" (вызываем метод напрямую)
        self.editor.apply_changes(None)

        # ПРОВЕРКИ
        # 1. Проверяем, что переход создался в графе
        self.assertEqual(len(self.app.graph.transitions), 1)
        transition = list(self.app.graph.transitions)[0]
        self.assertEqual(transition.start.name, "q0")
        self.assertEqual(transition.end.name, "q1")
        self.assertEqual(transition.symbols, "a")

        # 2. Проверяем статусное сообщение
        self.assertEqual(self.app.ui.status_text.value, "Таблица применена")
        
        # 3. Проверяем, что функция отрисовки была вызвана
        mock_draw.assert_called_once()

    def test_apply_invalid_state_error(self):
        self.editor.build_table_ui()
        input_field = self.editor.cell_fields.get(("q0", "a"))
        
        # Вводим несуществующее состояние q99
        input_field.value = "q99"
        self.editor.apply_changes(None)

        # Проверяем, что появилась ошибка в статусе и переходы не очистились/обновились
        self.assertIn("не существует", self.app.ui.status_text.value)

if __name__ == "__main__":
    unittest.main()