import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest

class DummyGraph:
    def __init__(self, val=0):
        self.val = val

class DummyDrawModule:
    called_with = None
    
    @classmethod
    def draw_nodes(cls, app):
        cls.called_with = app

    @classmethod
    def reset(cls):
        cls.called_with = None

class DummyGraphModule:
    Graph = DummyGraph

sys.modules['graph'] = DummyGraphModule
sys.modules['draw'] = DummyDrawModule

from graph_history import History

class DummyApp:
    def __init__(self, graph):
        self.graph = graph

@pytest.fixture(autouse=True)
def reset_draw():
    DummyDrawModule.reset()

def test_init():
    history = History(max_count=10)
    assert history.max_count == 10
    assert history.graph_buffer == []
    assert history.temp_stash == []

def test_add_within_limit():
    history = History(max_count=3)
    graph1 = DummyGraph(1)
    
    history.add(graph1)
    
    assert len(history.graph_buffer) == 1
    assert history.graph_buffer[0].val == 1
    assert history.graph_buffer[0] is not graph1

def test_add_exceeds_limit():
    history = History(max_count=2)
    
    history.add(DummyGraph(1))
    history.add(DummyGraph(2))
    history.add(DummyGraph(3))
    
    assert len(history.graph_buffer) == 2
    assert history.graph_buffer[0].val == 2
    assert history.graph_buffer[1].val == 3

def test_add_clears_temp_stash():
    history = History()
    history.temp_stash = [DummyGraph(1)]
    
    history.add(DummyGraph(2))
    
    assert history.temp_stash == []

def test_undo_click_empty():
    history = History()
    app = DummyApp(DummyGraph(1))
    
    history.undo_click(app)
    
    assert app.graph.val == 1
    assert len(history.temp_stash) == 0
    assert DummyDrawModule.called_with is None

def test_undo_click():
    history = History()
    app = DummyApp(DummyGraph(2))
    history.graph_buffer = [DummyGraph(1)]
    
    history.undo_click(app)
    
    assert app.graph.val == 1
    assert len(history.temp_stash) == 1
    assert history.temp_stash[0].val == 2
    assert len(history.graph_buffer) == 0
    assert DummyDrawModule.called_with is app

def test_redo_click_empty():
    history = History()
    app = DummyApp(DummyGraph(1))
    
    history.redo_click(app)
    
    assert app.graph.val == 1
    assert len(history.graph_buffer) == 0
    assert DummyDrawModule.called_with is None

def test_redo_click():
    history = History()
    app = DummyApp(DummyGraph(1))
    history.temp_stash = [DummyGraph(2)]
    
    history.redo_click(app)
    
    assert app.graph.val == 2
    assert len(history.graph_buffer) == 1
    assert history.graph_buffer[0].val == 1
    assert len(history.temp_stash) == 0
    assert DummyDrawModule.called_with is app