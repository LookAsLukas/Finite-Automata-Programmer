import math
from collections.abc import Iterable
from typing import List, Tuple, Dict, Set, Any
import igraph as ig


def prepare_automaton_layout(
    automaton,
    canvas_width: int = 700,
    canvas_height: int = 450,
    margin: int = 60,
) -> Tuple[List[Tuple[float, float]], List[str], Dict[int, List[Dict[str, Any]]], Set[int], int, Set[str]]:
    """
    Формирует расположение состояний автомата на плоскости (через igraph) и
    возвращает данные для отрисовки. При сбое расчета раскладки используется
    резервный круговой расклад.

    Returns:
        nodes: список координат (x, y) для состояний.
        state_names: список имен состояний, индекс соответствует nodes.
        transitions: словарь индекс -> список переходов {symbol, end}.
        final_state_indices: множество индексов конечных состояний.
        start_state_index: индекс стартового состояния.
        alphabet: множество допустимых символов.
    """
    if not hasattr(automaton, "states"):
        raise ValueError("Некорректный автомат: отсутствует поле states")

    states = sorted(automaton.states)
    initial_state = getattr(automaton, "initial_state", None)

    if initial_state in states:
        states.remove(initial_state)
        states.insert(0, initial_state)

    state_to_index = {state: idx for idx, state in enumerate(states)}
    count = len(states)
    center_x = canvas_width / 2
    center_y = canvas_height / 2

    def _fallback_circle_layout() -> List[Tuple[float, float]]:
        """Возвращает координаты по окружности как запасной вариант."""
        nodes_circle = []
        radius = max(min(canvas_width, canvas_height) / 2 - margin, 80)
        for idx in range(count):
            angle = 2 * math.pi * idx / count
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            nodes_circle.append((x, y))
        return nodes_circle

    nodes: List[Tuple[float, float]] = []
    if count == 0:
        nodes = []
    elif count == 1:
        nodes = [(center_x, center_y)]
    else:
        edges: List[Tuple[int, int]] = []
        raw_transitions = getattr(automaton, "transitions", {})
        for start_state, transition_map in raw_transitions.items():
            if start_state not in state_to_index:
                continue
            for destinations in transition_map.values():
                dest_iterable = destinations if isinstance(destinations, Iterable) and not isinstance(destinations, (str, bytes)) else [destinations]
                for dest_state in dest_iterable:
                    if dest_state in state_to_index:
                        edges.append((state_to_index[start_state], state_to_index[dest_state]))

        graph = ig.Graph(directed=True)
        graph.add_vertices(states)
        if edges:
            graph.add_edges(edges)

        try:
            # Force-directed раскладка дает более естественный вид, чем круговой.
            layout = graph.layout_fruchterman_reingold() if edges else graph.layout_circle()
            coords = layout.coords
        except Exception:
            # Если что-то пошло не так, вернемся к резервному кругу.
            nodes = _fallback_circle_layout()
            coords = []

        if coords:
            xs = [x for x, _ in coords]
            ys = [y for _, y in coords]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            span_x = max(max_x - min_x, 1e-6)
            span_y = max(max_y - min_y, 1e-6)

            usable_width = max(canvas_width - 2 * margin, 1)
            usable_height = max(canvas_height - 2 * margin, 1)
            scale = min(usable_width / span_x, usable_height / span_y)

            nodes = [
                (
                    center_x + (x - (min_x + max_x) / 2) * scale,
                    center_y + (y - (min_y + max_y) / 2) * scale,
                )
                for x, y in coords
            ]

    transitions: Dict[int, List[Dict[str, Any]]] = {}
    raw_transitions = getattr(automaton, "transitions", {})

    for start_state, transition_map in raw_transitions.items():
        if start_state not in state_to_index:
            continue
        start_index = state_to_index[start_state]
        for symbol, destinations in transition_map.items():
            if isinstance(destinations, Iterable) and not isinstance(destinations, (str, bytes)):
                dest_iterable = destinations
            else:
                dest_iterable = [destinations]
            for dest_state in dest_iterable:
                if dest_state not in state_to_index:
                    continue
                end_index = state_to_index[dest_state]
                transitions.setdefault(start_index, []).append({"symbol": symbol, "end": end_index})

    final_state_indices = {
        state_to_index[state]
        for state in getattr(automaton, "final_states", set())
        if state in state_to_index
    }

    start_state_index = state_to_index.get(initial_state) if initial_state is not None else None
    alphabet = set(getattr(automaton, "input_symbols", set()))

    return nodes, states, transitions, final_state_indices, start_state_index, alphabet

import igraph as ig

def convert_automaton_to_igraph(attr):
    g = ig.Graph(directed=True)
    g.add_vertices(attr.states)
    edges = []
    labels = []
    for (src, symbol), dst_list in attr.transitions.items():
        for dst in dst_list:
            edges.append((src, dst))
            labels.append(symbol)
    g.add_edges(edges)
    g.es["label"] = labels
    return g