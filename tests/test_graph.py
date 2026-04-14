import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from graph import Node, NodeType, Transition, Graph


def test_node_initialization():
    node = Node(x=10.5, y=20.0, name="q0")
    
    assert node.x == 10.5
    assert node.y == 20.0
    assert node.name == "q0"
    assert node.type == NodeType.NORMAL

def test_node_identity_semantics():
    node1 = Node(x=0.0, y=0.0, name="q1")
    node2 = Node(x=0.0, y=0.0, name="q1")
    
    assert node1 is not node2
    assert node1 != node2
    
    node_set = {node1, node2}
    assert len(node_set) == 2


def test_transition_initialization():
    start_node = Node(x=0.0, y=0.0, name="q0", type=NodeType.START)
    end_node = Node(x=10.0, y=10.0, name="q1", type=NodeType.FINAL)
    
    transition = Transition(start=start_node, end=end_node, symbols="a,b")
    
    assert transition.start == start_node
    assert transition.end == end_node
    assert transition.symbols == "a,b"

def test_transition_identity_semantics():
    n1 = Node(x=0, y=0, name="1")
    n2 = Node(x=1, y=1, name="2")
    
    t1 = Transition(start=n1, end=n2, symbols="x")
    t2 = Transition(start=n1, end=n2, symbols="x")
    
    assert t1 is not t2
    assert t1 != t2


@pytest.fixture
def populated_graph():
    g = Graph()
    
    n_normal = Node(0, 0, "normal", NodeType.NORMAL)
    n_start = Node(0, 0, "start", NodeType.START)
    n_final = Node(0, 0, "final", NodeType.FINAL)
    n_start_final = Node(0, 0, "start_final", NodeType.START_FINAL)
    
    g.nodes.update([n_normal, n_start, n_final, n_start_final])
    
    nodes_dict = {
        "normal": n_normal,
        "start": n_start,
        "final": n_final,
        "start_final": n_start_final
    }
    return g, nodes_dict

def test_graph_default_initialization():
    g = Graph()
    
    assert isinstance(g.nodes, set)
    assert len(g.nodes) == 0
    assert isinstance(g.transitions, set)
    assert len(g.transitions) == 0
    assert g.node_counter == 0
    assert g.selected_node is None
    assert g.selected_transition is None
    assert g.dragging_node is None

def test_graph_get_final_states(populated_graph):
    g, nodes = populated_graph
    
    final_states = g.get_final_states()
    
    assert len(final_states) == 2
    assert nodes["final"] in final_states
    assert nodes["start_final"] in final_states
    assert nodes["normal"] not in final_states
    assert nodes["start"] not in final_states

def test_graph_get_start_states(populated_graph):
    g, nodes = populated_graph
    
    start_states = g.get_start_states()
    
    assert len(start_states) == 2
    assert nodes["start"] in start_states
    assert nodes["start_final"] in start_states
    assert nodes["normal"] not in start_states
    assert nodes["final"] not in start_states

def test_empty_graph_get_states():
    g = Graph()
    
    assert g.get_final_states() == set()
    assert g.get_start_states() == set()