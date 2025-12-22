from automata.fa.nfa import NFA
from automata_visualizer import prepare_automaton_layout
from application_state import EPSILON_SYMBOL

def build_nfa_from_ui(attr):
    """
    Создает объект NFA, автоматически отфильтровывая переходы 
    в удаленные/несуществующие состояния.
    """
    if not attr.nodes or attr.start_state is None:
        return None

    states = set(attr.nodes.keys())
    
    if attr.start_state not in states:
        return None

    nfa_transitions = {}
    
    for start_name, trans_list in attr.transitions.items():
        if start_name not in states:
            continue
            
        nfa_transitions[start_name] = {}
        
        for t in trans_list:
            symbol_ui = t["symbol"]
            end_name = t["end"]
            
            if end_name not in states:
                continue
            
            logic_symbol = "" if symbol_ui == EPSILON_SYMBOL else symbol_ui
            
            nfa_transitions[start_name].setdefault(logic_symbol, set()).add(end_name)

    for name in states:
        if name not in nfa_transitions:
            nfa_transitions[name] = {}

    try:
        input_symbols = {s for s in attr.alphabet if s != EPSILON_SYMBOL}

        return NFA(
            states=states,
            input_symbols=input_symbols,
            transitions=nfa_transitions,
            initial_state=attr.start_state,
            final_states={s for s in attr.final_states if s in states}
        )
    except Exception as e:
        print(f"Ошибка создания NFA: {e}")
        return None


def import_automaton_data(automaton, attr, ui):
    """
    Импортирует данные из объекта DFA/NFA в атрибуты приложения.
    """
    try:
        layout_nodes, layout_state_names, layout_transitions, layout_final_states, layout_start_index, layout_alphabet = prepare_automaton_layout(automaton)
        
        attr.nodes.clear()
        attr.final_states.clear()
        attr.transitions.clear()
        attr.alphabet.clear()

        string_names = [str(name) for name in layout_state_names]
        
        for i, (x, y) in enumerate(layout_nodes):
            name = string_names[i]
            attr.nodes[name] = (x, y)
            
        attr.transitions = {}
        for start_idx, trans_list in layout_transitions.items():
            start_name = string_names[start_idx]
            attr.transitions[start_name] = []
            for t in trans_list:
                end_name = string_names[t["end"]]
                ui_symbol = EPSILON_SYMBOL if t["symbol"] == "" else t["symbol"]
                attr.transitions[start_name].append({"symbol": ui_symbol, "end": end_name})

        if layout_start_index is not None:
            attr.start_state = string_names[layout_start_index]
        else:
            attr.start_state = None
            
        attr.final_states = {string_names[i] for i in layout_final_states}
        
        attr.node_counter = len(string_names)
        for s in layout_alphabet:
            if s != "":
                attr.alphabet.add(s)
                
        attr.placing_mode = False
        attr.transition_mode = False
        attr.selected_node = None
        attr.first_selected_node = None

        ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(attr.alphabet))}" if attr.alphabet else "Алфавит: ∅"
        ui.mode_status.value = "Режим размещения: выключен"
        ui.transition_status.value = "Режим переходов: выключен"
        ui.status_text.value = "Автомат успешно построен"

        return True
    except Exception as ex:
        ui.status_text.value = f"Ошибка при импорте автомата: {ex}"
        print(f"DEBUG ERROR: {ex}")
        return False