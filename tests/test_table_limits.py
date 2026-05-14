import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

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
        self.app.history = MagicMock()
        self.editor = TableEditor(self.app)
        self.editor.update_canvas = MagicMock()
        self.editor.refresh_ui = MagicMock()

    def test_add_row_increases_states(self):
        self.editor.add_row(None)
        self.assertEqual(len(self.editor.get_states()), 1)

    def test_delete_row_decreases_states(self):
        self.app.graph.nodes.add(Node(x=10, y=10, name="q0"))
        self.app.graph.nodes.add(Node(x=20, y=20, name="q1"))
        self.editor.delete_row(None)
        self.assertEqual(len(self.editor.get_states()), 1)

    def test_add_column_increases_symbols(self):
        self.app.attr.alphabet = {'a'}
        self.editor.add_column(None)
        self.assertEqual(len(self.editor.get_symbols()), 2)

    def test_delete_column_decreases_symbols(self):
        self.app.attr.alphabet = {'a', 'b'}
        self.editor.delete_column(None)
        self.assertEqual(len(self.editor.get_symbols()), 1)

if __name__ == "__main__":
    unittest.main()