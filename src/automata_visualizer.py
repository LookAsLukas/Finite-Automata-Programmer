import math
import igraph as ig
from graph import Node, Transition, Graph, NodeType
from fap import Application
from automata.fa.nfa import NFA
from linal import Vector2D


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

    igraph = ig.Graph(directed=True)
    igraph.add_vertices(nodes)
    igraph.add_edges(transitions)
    try:
        coords = graph.layout_fruchterman_reingold().coords
    except Exception:
        coords = [
            Vector2D.from_phi_r(i / len(nodes) * 2 * math.pi, 1).to_tuple()
            for i in range(len(nodes))
        ]

    frame_bottom_x = app.config.node_radius
    frame_bottom_y = app.config.node_radius
    frame_width = app.attr.canvas_width - 2 * app.config.node_radius
    frame_height = app.attr.canvas_height - 2 * app.config.node_radius

    picture_bottom_x = min(x for x, _ in coords)
    picture_bottom_y = min(y for _, y in coords)
    picture_width = max(x for x, _ in coords) - picture_bottom_x
    picture_height = max(y for _, y in coords) - picture_bottom_y

    coords = [
        (
            (x - picture_bottom_x) / picture_width * frame_width + frame_bottom_x if picture_width else frame_width / 2 + app.config.node_radius,
            (y - picture_bottom_y) / picture_height * frame_height + frame_bottom_y if picture_height else frame_height / 2 + app.config.node_radius,
        )
        for x, y in coords
    ]

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
