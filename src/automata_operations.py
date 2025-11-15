from automata.fa.nfa import NFA
from automata_visualizer import prepare_automaton_layout


def build_nfa_from_ui(attr):
    """Создает объект NFA из automata-lib на основе текущего автомата"""
    if not attr.nodes or attr.start_state is None:
        return None

    states = set(attr.nodes.keys())
    initial_state = attr.start_state
    final_state_names = attr.final_states

    nfa_transitions = {}
    for start_name, trans_list in attr.transitions.items():
        nfa_transitions[start_name] = {}
        for t in trans_list:
            symbol = t["symbol"]
            end_name = t["end"]
            nfa_transitions[start_name].setdefault(symbol, set()).add(end_name)

    for name in states:
        nfa_transitions.setdefault(name, {})

    return NFA(
        states=states,
        input_symbols=set(attr.alphabet),
        transitions=nfa_transitions,
        initial_state=initial_state,
        final_states=final_state_names,
    )


def import_automaton_data(automaton, attr, ui):
    """Импортирует данные автомата в UI"""
    try:
        layout = prepare_automaton_layout(automaton, canvas_width=700, canvas_height=450)
        layout_nodes, layout_state_names, layout_transitions, layout_final_states, layout_start_index, layout_alphabet = layout

        # Конвертируем формат данных из automata_visualizer в наш формат
        attr.nodes = {}
        for i, (x, y) in enumerate(layout_nodes):
            attr.nodes[layout_state_names[i]] = (x, y)
        
        attr.transitions = {}
        for start_idx, trans_list in layout_transitions.items():
            start_name = layout_state_names[start_idx]
            attr.transitions[start_name] = []
            for t in trans_list:
                end_name = layout_state_names[t["end"]]
                attr.transitions[start_name].append({"symbol": t["symbol"], "end": end_name})
        
        attr.final_states = {layout_state_names[i] for i in layout_final_states}
        attr.start_state = layout_state_names[layout_start_index] if layout_start_index is not None else None
        attr.alphabet = set(layout_alphabet)
        attr.node_counter = len(layout_state_names)
        attr.placing_mode = False
        attr.transition_mode = False
        attr.selected_node = None
        attr.first_selected_node = None

        ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(attr.alphabet))}" if attr.alphabet else "Алфавит: ∅"
        ui.mode_status.value = "Режим размещения: выключен"
        ui.transition_status.value = "Режим переходов: выключен"
        ui.status_text.value = "✅ Автомат импортирован из nfa.json"

        return True
    except Exception as ex:
        ui.status_text.value = f"Ошибка при импорте автомата: {ex}"
        return False
