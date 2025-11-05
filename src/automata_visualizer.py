import math
from collections.abc import Iterable
from typing import List, Tuple, Dict, Set, Any


def prepare_automaton_layout(
    automaton,
    canvas_width: int = 700,
    canvas_height: int = 450,
    margin: int = 60,
) -> Tuple[List[Tuple[float, float]], List[str], Dict[int, List[Dict[str, Any]]], Set[int], int, Set[str]]:
    """
    Формирует простое расположение состояний автомата на плоскости и возвращает данные
    для отрисовки.

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
    nodes = []
    count = len(states)

    center_x = canvas_width / 2
    center_y = canvas_height / 2
    radius = max(min(canvas_width, canvas_height) / 2 - margin, 80)

    if count == 1:
        nodes.append((center_x, center_y))
    else:
        for idx in range(count):
            angle = 2 * math.pi * idx / count
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            nodes.append((x, y))

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

