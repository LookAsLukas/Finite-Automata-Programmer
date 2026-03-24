from graph import Graph
from typing import List
from copy import deepcopy


class History:
    graph_buffer: List[Graph]
    temp_stash: List[Graph]
    max_count: int

    def __init__(self, max_count: int = 30):
        self.graph_buffer = []
        self.temp_stash = []
        self.max_count = max_count

    def add(self, action: Graph):
        if len(self.graph_buffer) == self.max_count:
            self.graph_buffer = self.graph_buffer[1:]
        self.temp_stash = []
        self.graph_buffer.append(deepcopy(action))

    def undo_click(self, app):
        if len(self.graph_buffer) == 0:
            return

        self.temp_stash.append(deepcopy(app.graph))
        app.graph = self.graph_buffer.pop()
        from draw import draw_nodes
        draw_nodes(app)

    def redo_click(self, app):
        if len(self.temp_stash) == 0:
            return

        self.graph_buffer.append(deepcopy(app.graph))
        app.graph = self.temp_stash.pop()
        from draw import draw_nodes
        draw_nodes(app)
