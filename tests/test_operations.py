import pytest
import sys
import os
from automata_operations import build_nfa_from_ui, import_automaton_data
from application_state import ApplicationAttributes, ApplicationUI
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from json import load
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_build():
    attr = ApplicationAttributes()
    attr.nodes = {"a": (0, 1), "b": (69, 69), "c": (228, 1337)}
    attr.start_state = "a"
    attr.final_states = {"b", "c"}
    attr.transitions = {
        "a": [{"symbol": '0', "end": "b"}, {"symbol": '1', "end": "c"}],
        "b": [{"symbol": '1', "end": "c"}]
    }
    attr.alphabet = {'0', '1'}
    got = build_nfa_from_ui(attr)
    fa = NFA(
        states={'a', 'b', 'c'},
        input_symbols={'0', '1'},
        transitions={
            'a': {
                '1': {'c'},
                '0': {'b'},
            },
            'b': {
                '1': {'c'},
            },
        },
        initial_state='a',
        final_states={'b', 'c'}
    )
    assert fa == got


def test_build_none():
    attr = ApplicationAttributes()
    assert build_nfa_from_ui(attr) is None
    attr.nodes = {"a": (0, 1), "b": (69, 69), "c": (228, 1337)}
    assert build_nfa_from_ui(attr) is None


def test_import():
    got_attr = ApplicationAttributes()
    got_ui = ApplicationUI()
    fa = NFA(
        states={'a', 'b', 'c'},
        input_symbols={'0', '1'},
        transitions={
            'a': {
                '1': {'c'},
                '0': {'b'},
            },
            'b': {
                '1': {'c'},
            },
        },
        initial_state='a',
        final_states={'b', 'c'}
    )
    import_automaton_data(fa, got_attr, got_ui)
    attr = ApplicationAttributes()
    attr.nodes = {"a": (0, 1), "b": (69, 69), "c": (228, 1337)}
    attr.start_state = "a"
    attr.final_states = {"b", "c"}
    attr.transitions = {
        "a": [{"symbol": '0', "end": "b"}, {"symbol": '1', "end": "c"}],
        "b": [{"symbol": '1', "end": "c"}]
    }
    attr.alphabet = {'0', '1'}
    assert attr == got_attr


