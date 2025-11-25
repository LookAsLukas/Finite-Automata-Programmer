import pytest
import sys
import os
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from json import load
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from canvas_utils import get_clicked_node, get_clicked_transition


def test_node():
    nodes = {"a": (0, 0), "b": (69, 69), "c": (228, 1337)}
    assert "b" == get_clicked_node(69.0069, 69.0069, nodes)


def test_node_miss():
    nodes = {"a": (0, 0), "b": (69, 69), "c": (228, 1337)}
    assert None is get_clicked_node(-52, -52, nodes)


def test_transition():
    nodes = {"a": (0, 0), "b": (69, 69), "c": (228, 1337)}
    transitions = {
        "a": [{"symbol": '0', "end": "b"}, {"symbol": '1', "end": "c"}],
        "b": [{"symbol": '1', "end": "c"}]
    }
    assert ("a", {"symbol": '0', "end": "b"}) == get_clicked_transition(52, 52, nodes, transitions)


def test_transition_miss():
    nodes = {"a": (0, 0), "b": (69, 69), "c": (228, 1337)}
    transitions = {
        "a": [{"symbol": '0', "end": "b"}, {"symbol": '1', "end": "c"}],
        "b": [{"symbol": '1', "end": "c"}]
    }
    assert (None, None) == get_clicked_transition(228, 69, nodes, transitions)
