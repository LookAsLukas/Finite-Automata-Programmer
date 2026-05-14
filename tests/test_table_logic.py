import unittest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from table import TableEditor
from graph import Graph, Node, Transition
from application_state import ApplicationState, ApplicationUI

class TestTableLogic(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.app.graph = Graph()
        self.app.attr = ApplicationState()
        self.app.ui = ApplicationUI()
        self.app.page = MagicMock()
        self.app.history = MagicMock()
        self.app.ui.status_text = MagicMock()
        self.node_q0 = Node(x=10, y=10, name="q0")
        self.node_q1 = Node(x=20, y=20, name="q1")
        self.app.graph.nodes = {self.node_q0, self.node_q1}
        self.app.attr.alphabet = {'a'}
        self.editor = TableEditor(self.app)
        self.editor.update_canvas = MagicMock()
        self.editor.refresh_ui = MagicMock()

    def test_get_states_returns_sorted_names(self):
        states = self.editor.get_states()
        self.assertIn("q0", states)
        self.assertIn("q1", states)

    def test_get_symbols_returns_alphabet(self):
        symbols = self.editor.get_symbols()
        self.assertIn('a', symbols)

    def test_get_transition_map_returns_correct_structure(self):
        self.app.graph.transitions.add(Transition(start=self.node_q0, end=self.node_q1, symbols='a'))
        tr_map = self.editor.get_transition_map()
        self.assertIn(("q0", "a"), tr_map)
        self.assertIn("q1", tr_map[("q0", "a")])

    @patch('table.ft.TextField')
    def test_edit_cell_creates_transition(self, mock_tf):
        self.app.graph.transitions = set()
        mock_tf.return_value.value = "q1"
        self.editor.edit_cell("q0", "a", "")
        dialog = self.app.page.open.call_args[0][0]
        save_callback = dialog.actions[1].on_click
        save_callback(MagicMock())
        self.assertEqual(len(self.app.graph.transitions), 1)
        tr = list(self.app.graph.transitions)[0]
        self.assertEqual(tr.start.name, "q0")
        self.assertEqual(tr.end.name, "q1")
        self.assertEqual(tr.symbols, "a")

    @patch('table.ft.TextField')
    def test_edit_cell_invalid_state_shows_error(self, mock_tf):
        self.app.graph.transitions = set()
        mock_tf.return_value.value = "q99"
        self.editor.edit_cell("q0", "a", "")
        dialog = self.app.page.open.call_args[0][0]
        save_callback = dialog.actions[1].on_click
        save_callback(MagicMock())
        self.assertIn("не существует", self.app.ui.status_text.value)

if __name__ == "__main__":
    unittest.main()