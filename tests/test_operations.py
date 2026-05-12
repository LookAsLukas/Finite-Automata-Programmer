import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from automata_operations import (
    _is_wrapped,
    _wrap_if_needed,
    _union_regex,
    _concat_regex,
    _star_regex,
    simplify_regex,
    nfa_to_regex_state_elimination,
    EPSILON_SYMBOL
)


class MockNode:
    def __init__(self, name):
        self.name = name

class MockTransition:
    def __init__(self, start, end, symbols):
        self.start = start
        self.end = end
        self.symbols = symbols

class MockGraph:
    def __init__(self, nodes, transitions, starts, finals):
        self.nodes = nodes
        self.transitions = transitions
        self.starts = starts
        self.finals = finals
    def get_start_states(self): return self.starts
    def get_final_states(self): return self.finals

class MockApp:
    def __init__(self, graph):
        self.graph = graph
        self.attr = type('obj', (object,), {'alphabet': set()})
        self.ui = type('obj', (object,), {
            'status_text': type('obj', (object,), {'value': ''}),
            'alphabet_display': type('obj', (object,), {'value': ''})
        })
        self.history = type('obj', (object,), {
            'add': lambda x: None,
            'remove': lambda: None
        })


@pytest.mark.parametrize("regex, expected", [
    ("(a|b)", True),
    ("a|b", False),
    ("(a)(b)", False),
    ("((a))", True),
])
def test_wrapping_logic(regex, expected):
    assert _is_wrapped(regex) == expected
    if not expected:
        assert _wrap_if_needed(regex) == f"({regex})"

def test_union_regex():
    assert _union_regex("a", "b") == "a|b"
    assert _union_regex("a", "a") == "a"
    assert _union_regex(None, "b") == "b"

def test_concat_regex():
    assert _concat_regex("a", "b") == "ab"
    assert _concat_regex("a|b", "c") == "(a|b)c"
    assert _concat_regex(EPSILON_SYMBOL, "a") == "a"

def test_star_regex():
    assert _star_regex("a") == "a*"
    assert _star_regex("a|b") == "(a|b)*"
    assert _star_regex(EPSILON_SYMBOL) == EPSILON_SYMBOL


@pytest.mark.parametrize("input_reg, expected", [
    ("((a))", "a"),
    ("ε*", "ε"),
    ("a|∅", "a"),
    ("aε", "a"),
    ("a**", "a*"),
    ("(ε|a*)", "a*"),
    ("a|a", "a"),
])
def test_simplify_regex_logic(input_reg, expected):
    assert simplify_regex(input_reg) == expected


def test_state_elimination_basic():

    class SimpleNFA:
        def __init__(self):
            self.states = {'q0', 'q1'}
            self.initial_state = 'q0'
            self.final_states = {'q1'}
            self.transitions = {'q0': {'a': {'q1'}}, 'q1': {'b': {'q1'}}}
            self.input_symbols = {'a', 'b'}

    nfa = SimpleNFA()
    result = nfa_to_regex_state_elimination(nfa)
    
    clean_result = result.replace("(", "").replace(")", "")
    assert "ab*" in clean_result



def test_build_nfa_logic():
    from automata_operations import build_nfa_from_ui
    
    q0, q1 = MockNode("q0"), MockNode("q1")
    trans = MockTransition(q0, q1, ['a'])
    graph = MockGraph({q0, q1}, [trans], {q0}, {q1})
    app = MockApp(graph)
    app.attr.alphabet = {'a'}
    
    nfa = build_nfa_from_ui(app)
    
    assert nfa is not None
    assert "q0" in nfa.states
    assert "q1" in nfa.states

    assert nfa.transitions["q0"]["a"] == {"q1"}