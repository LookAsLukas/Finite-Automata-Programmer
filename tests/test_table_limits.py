import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from table import TableEditor
from graph import Graph, Node
from application_state import ApplicationState, ApplicationUI

class TestTableLimits(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.graph = Graph()
        self.app.attr = ApplicationState()
        self.app.ui = ApplicationUI()
        self.app.page = MagicMock()
        
        self.editor = TableEditor(self.app)

    def test_max_states_limit(self):
        # Искусственно заполняем список состояний до лимита
        self.editor.states = [f"q{i}" for i in range(10)]
        
        # Пытаемся добавить 11-ю строку
        self.editor.add_row(None)
        
        # Проверяем, что количество не увеличилось
        self.assertEqual(len(self.editor.states), 10)

    def test_delete_row(self):
        # Начальное состояние: 2 узла
        self.editor.states = ["q0", "q1"]
        self.editor.build_table_ui()
        
        # Удаляем строку
        self.editor.delete_row(None)
        
        # Проверяем, что осталось 1 состояние
        self.assertEqual(len(self.editor.states), 1)
        self.assertEqual(self.editor.states[0], "q0")

    def test_max_symbols_limit(self):
        # Заполняем алфавит до лимита
        self.editor.symbols = [chr(97 + i) for i in range(10)] # a, b, c...
        
        # Пытаемся добавить столбец
        self.editor.add_column(None)
        
        # Проверяем лимит
        self.assertEqual(len(self.editor.symbols), 10)

    def test_delete_column(self):
        self.editor.symbols = ["a", "b"]
        self.editor.build_table_ui()
        
        self.editor.delete_column(None)
        
        self.assertEqual(len(self.editor.symbols), 1)
        self.assertEqual(self.editor.symbols[0], "a")

if __name__ == "__main__":
    unittest.main()