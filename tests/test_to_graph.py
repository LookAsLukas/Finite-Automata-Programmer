import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
import igraph as ig
from automation_to_graph import convert_automaton_to_igraph

class MockAutomaton:
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions

def test_convert_automaton_to_igraph():
    states = ['q0', 'q1', 'q2']
    
    transitions = {
        ('q0', 'a'): ['q1', 'q2'],
        ('q1', 'b'): ['q2'],
        ('q2', 'c'): ['q0']
    }
    
    mock_attr = MockAutomaton(states, transitions)

    g = convert_automaton_to_igraph(mock_attr)

    assert g.is_directed() is True, "Graph should be directed"
    assert g.vcount() == 3, "Number of vertices should be 3"
    assert list(g.vs["name"]) == states, "Vertex names should match states"

    assert g.ecount() == 4, "Number of edges should be 4 (one branching)"

    edges_with_labels = []
    for edge in g.es:
        source_name = g.vs[edge.source]["name"]
        target_name = g.vs[edge.target]["name"]
        label = edge["label"]
        edges_with_labels.append(((source_name, target_name), label))

    expected_edges = [
        (('q0', 'q1'), 'a'),
        (('q0', 'q2'), 'a'),
        (('q1', 'q2'), 'b'),
        (('q2', 'q0'), 'c')
    ]

    for expected in expected_edges:
        assert expected in edges_with_labels, f"Expected transition {expected} not found in graph"

def test_empty_automaton():
    mock_attr = MockAutomaton(states=[], transitions={})
    g = convert_automaton_to_igraph(mock_attr)

    assert g.is_directed() is True
    assert g.vcount() == 0
    assert g.ecount() == 0

def test_disconnected_states():
    states = ['q0', 'q1', 'q2', 'q3']
    mock_attr = MockAutomaton(states=states, transitions={})
    g = convert_automaton_to_igraph(mock_attr)

    assert g.is_directed() is True
    assert g.vcount() == 4
    assert list(g.vs["name"]) == states
    assert g.ecount() == 0

def test_single_state_self_loop():
    states = ['q0']
    transitions = {
        ('q0', 'a'): ['q0'],
        ('q0', 'b'): ['q0']
    }
    mock_attr = MockAutomaton(states=states, transitions=transitions)
    g = convert_automaton_to_igraph(mock_attr)

    assert g.is_directed() is True
    assert g.vcount() == 1
    assert g.ecount() == 2

    edges_with_labels = []
    for edge in g.es:
        source_name = g.vs[edge.source]["name"]
        target_name = g.vs[edge.target]["name"]
        label = edge["label"]
        edges_with_labels.append(((source_name, target_name), label))

    expected_edges = [
        (('q0', 'q0'), 'a'),
        (('q0', 'q0'), 'b')
    ]

    for expected in expected_edges:
        assert expected in edges_with_labels