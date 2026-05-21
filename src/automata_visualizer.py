from __future__ import annotations

import math
import igraph as ig
from graph import Node, Transition, Graph, NodeType
from automata.fa.nfa import NFA
from linal import Vector2D


def layout_graph_nodes(graph: Graph, app: Application) -> None:
    """Place existing graph nodes using the same igraph layout as automaton import."""
    nodes = sorted(graph.nodes, key=lambda node: str(node.name))
    if not nodes:
        return

    node_to_ind = {node: ind for ind, node in enumerate(nodes)}
    transitions = [
        (node_to_ind[transition.start], node_to_ind[transition.end])
        for transition in graph.transitions
        if transition.start in node_to_ind and transition.end in node_to_ind
    ]

    coords = _calculate_layout_coords(
        [node.name for node in nodes],
        transitions,
        app,
    )

    for node, (x, y) in zip(nodes, coords):
        node.x = x
        node.y = y


def _calculate_layout_coords(names, transitions, app: Application):
    if not names:
        return []

    igraph = ig.Graph(directed=True)
    igraph.add_vertices(names)
    igraph.add_edges(transitions)
    try:
        coords = igraph.layout_fruchterman_reingold().coords
    except Exception:
        coords = [
            Vector2D.from_phi_r(i / len(names) * 2 * math.pi, 1).to_tuple()
            for i in range(len(names))
        ]

    return _fit_coords_to_canvas(coords, app)


def _fit_coords_to_canvas(coords, app: Application):
    if not coords:
        return []

    node_radius = getattr(getattr(app, "config", None), "node_radius", 30)
    if not isinstance(node_radius, (int, float)):
        node_radius = 30

    canvas_width = getattr(getattr(app, "attr", None), "canvas_width", 700)
    if not isinstance(canvas_width, (int, float)):
        canvas_width = 700

    canvas_height = getattr(getattr(app, "attr", None), "canvas_height", 450)
    if not isinstance(canvas_height, (int, float)):
        canvas_height = 450

    padding_coef = 3
    frame_bottom_x = padding_coef * node_radius
    frame_bottom_y = padding_coef * node_radius
    frame_width = canvas_width - padding_coef * 2 * node_radius
    frame_height = canvas_height - padding_coef * 2 * node_radius

    picture_bottom_x = min(x for x, _ in coords)
    picture_bottom_y = min(y for _, y in coords)
    picture_width = max(x for x, _ in coords) - picture_bottom_x
    picture_height = max(y for _, y in coords) - picture_bottom_y

    if picture_width == 0:
        picture_width = 1
    if picture_height == 0:
        picture_height = 1

    return [
        (
            (x - picture_bottom_x) / picture_width * frame_width + frame_bottom_x,
            (y - picture_bottom_y) / picture_height * frame_height + frame_bottom_y,
        )
        for x, y in coords
    ]


def automaton_to_graph(automaton: NFA, app: Application) -> Graph:
    """
    IMPORTANT: automaton must have a fantom "" named node, that
    points to all the start nodes via epsilon transitions
    """
    graph = Graph()

    start_nodes = {node for node in set().union(*automaton.transitions[""].values())}

    nodes = list(automaton.states)
    nodes.remove("")
    node_to_ind = {node: ind for ind, node in enumerate(nodes)}
    transitions = [
        (node_to_ind[start], node_to_ind[end])
        for start in nodes
        for end in set().union(*automaton.transitions[start].values())
    ]

    coords = _calculate_layout_coords(nodes, transitions, app)

    nodes = [
        Node(
            x=x, y=y,
            name=name
        )
        for name, (x, y) in zip(nodes, coords)
    ]
    for node in nodes:
        if node.name in start_nodes and node.name in automaton.final_states:
            node.type = NodeType.START_FINAL
        elif node.name in start_nodes:
            node.type = NodeType.START
        elif node.name in automaton.final_states:
            node.type = NodeType.FINAL

    from automata_operations import EPSILON_SYMBOL
    transitions = [
        Transition(
            start=nodes[start_ind],
            end=nodes[end_ind],
            symbols=''.join(
                symbol if symbol != '' else EPSILON_SYMBOL
                for symbol in automaton.transitions[nodes[start_ind].name]
                if nodes[end_ind].name in automaton.transitions[nodes[start_ind].name][symbol]
            )
        )
        for start_ind, end_ind in transitions
    ]

    graph.nodes = set(nodes)
    graph.transitions = set(transitions)
    graph.node_counter = len(nodes)
    return graph
