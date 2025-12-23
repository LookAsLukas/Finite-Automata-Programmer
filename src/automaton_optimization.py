from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from application_state import EPSILON_SYMBOL
from automata_operations import import_automaton_data

def get_complete_alphabet(attr):
    symbols = {s for s in attr.alphabet if s not in ("", EPSILON_SYMBOL)}
    for trans_list in attr.transitions.values():
        for t in trans_list:
            symbol = t["symbol"]
            if symbol in ("", EPSILON_SYMBOL):
                continue
            symbols.add(symbol)
    return symbols

def safe_build_nfa(attr, ui):
    if not attr.nodes or attr.start_state is None:
        return None

    states = set(attr.nodes.keys())
    if attr.start_state not in states:
        return None

    complete_alphabet = get_complete_alphabet(attr)
    
    nfa_transitions = {}
    for s in states:
        nfa_transitions[s] = {}

    for start_name, trans_list in attr.transitions.items():
        if start_name not in states: continue
        
        for t in trans_list:
            symbol = t["symbol"]
            end_name = t["end"]
            
            if end_name not in states:
                continue
            
            logic_symbol = "" if symbol == EPSILON_SYMBOL else symbol
            if logic_symbol not in nfa_transitions[start_name]:
                nfa_transitions[start_name][logic_symbol] = set()
            nfa_transitions[start_name][logic_symbol].add(end_name)

    valid_finals = {s for s in attr.final_states if s in states}

    try:
        return NFA(
            states=states,
            input_symbols=complete_alphabet,
            transitions=nfa_transitions,
            initial_state=attr.start_state,
            final_states=valid_finals,
        )
    except Exception as e:
        print(f"Build NFA Error: {e}")
        return None

def is_deterministic(attr):
    for start_name, trans_list in attr.transitions.items():
        seen = {}
        for t in trans_list:
            symbol = t["symbol"]
            if symbol == EPSILON_SYMBOL:
                return False
            end_name = t["end"]
            if symbol in seen and seen[symbol] != end_name:
                return False
            seen[symbol] = end_name
    return True

def safe_build_dfa(attr):
    if not attr.nodes or attr.start_state is None:
        return None

    states = set(attr.nodes.keys())
    if attr.start_state not in states:
        return None

    complete_alphabet = get_complete_alphabet(attr)
    dfa_transitions = {s: {} for s in states}

    for start_name, trans_list in attr.transitions.items():
        if start_name not in states:
            continue
        for t in trans_list:
            symbol = t["symbol"]
            end_name = t["end"]
            if symbol == EPSILON_SYMBOL:
                return None
            if end_name not in states:
                continue
            if symbol in dfa_transitions[start_name] and dfa_transitions[start_name][symbol] != end_name:
                return None
            dfa_transitions[start_name][symbol] = end_name

    valid_finals = {s for s in attr.final_states if s in states}

    try:
        return DFA(
            states=states,
            input_symbols=complete_alphabet,
            transitions=dfa_transitions,
            initial_state=attr.start_state,
            final_states=valid_finals,
            allow_partial=True,
        )
    except Exception as e:
        print(f"Build DFA Error: {e}")
        return None

def ensure_dfa_complete(dfa):
    new_transitions = {
        state: dict(trans.items()) 
        for state, trans in dfa.transitions.items()
    }
    
    new_states = set(dfa.states)
    alphabet = dfa.input_symbols
    
    trap_state = frozenset({'TRAP_STATE'}) 
    
    trap_needed = False

    for state in list(new_states):
        if state not in new_transitions:
            new_transitions[state] = {}
        
        for symbol in alphabet:
            if symbol not in new_transitions[state]:
                new_transitions[state][symbol] = trap_state
                trap_needed = True

    if trap_needed:
        new_states.add(trap_state)
        if trap_state not in new_transitions:
            new_transitions[trap_state] = {}
        
        for symbol in alphabet:
            new_transitions[trap_state][symbol] = trap_state

    return DFA(
        states=new_states,
        input_symbols=alphabet,
        transitions=new_transitions,
        initial_state=dfa.initial_state,
        final_states=dfa.final_states
    )

def rename_states_sequentially(automaton):
    old_states = sorted(list(automaton.states), key=lambda x: str(x))
    
    if automaton.initial_state in old_states:
        old_states.remove(automaton.initial_state)
        old_states.insert(0, automaton.initial_state)
    
    mapping = {}
    for i, state in enumerate(old_states):
        mapping[state] = f"q{i}"
        
    new_transitions = {}
    for src, transitions in automaton.transitions.items():
        new_src = mapping[src]
        new_transitions[new_src] = {}
        for symbol, dst in transitions.items():
            if dst in mapping:
                new_transitions[new_src][symbol] = mapping[dst]
            
    allow_partial = getattr(automaton, "allow_partial", False)

    return DFA(
        states={mapping[s] for s in automaton.states},
        input_symbols=automaton.input_symbols,
        transitions=new_transitions,
        initial_state=mapping[automaton.initial_state],
        final_states={mapping[s] for s in automaton.final_states if s in mapping},
        allow_partial=allow_partial,
    )

def handle_optimize_click(e, attr, ui, page):
    if attr.start_state is None:
        ui.status_text.value = "Ошибка: выберите начальное состояние!"
        page.update()
        return

    ui.status_text.value = "Оптимизация..."
    page.update()

    try:
        nfa = safe_build_nfa(attr, ui)
        if nfa is None:
            ui.status_text.value = "Ошибка построения NFA (проверьте граф)"
            page.update()
            return

        if is_deterministic(attr):
            dfa_partial = safe_build_dfa(attr)
            if dfa_partial is None:
                ui.status_text.value = "Ошибка построения DFA (проверьте переходы)"
                page.update()
                return
            dfa_minimized = dfa_partial.minify()
            clean_dfa = rename_states_sequentially(dfa_minimized)
        else:
            dfa_partial = DFA.from_nfa(nfa)
            dfa_complete = ensure_dfa_complete(dfa_partial)
            clean_dfa = rename_states_sequentially(dfa_complete)

        saved_regex = attr.regex
        from draw import draw_nodes
        
        if import_automaton_data(clean_dfa, attr, ui):
            attr.regex = saved_regex
            draw_nodes(attr, ui)
            ui.status_text.value = "Оптимизация выполнена успешно!"
        else:
            ui.status_text.value = "Ошибка отрисовки результата"

    except Exception as ex:
        error_msg = str(ex)
        if "frozendict" in error_msg:
            error_msg = "Внутренняя ошибка библиотеки (frozendict)"
        ui.status_text.value = f"Сбой: {error_msg}"
        print(f"FULL ERROR: {ex}")
    
    page.update()
