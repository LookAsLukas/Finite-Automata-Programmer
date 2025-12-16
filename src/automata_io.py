import json
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from application_state import EPSILON_SYMBOL

def save_automaton_to_json(automaton, file_path, regex=""):
    """
    Сохраняет объект конечного автомата (DFA или NFA) в файл JSON.
    """
    if not isinstance(automaton, (DFA, NFA)):
        raise TypeError("Объект должен быть экземпляром DFA или NFA")

    is_dfa = isinstance(automaton, DFA)

    transitions_for_json = automaton.transitions
    
    if not is_dfa:
        transitions_for_json = {
            state: {
                symbol: list(dest_states)
                for symbol, dest_states in transitions.items()
            }
            for state, transitions in automaton.transitions.items()
        }

    automaton_dict = {
        'type': 'DFA' if is_dfa else 'NFA',
        'states': sorted(list(automaton.states)),
        'input_symbols': sorted(list(automaton.input_symbols)),
        'transitions': transitions_for_json,
        'initial_state': automaton.initial_state,
        'final_states': sorted(list(automaton.final_states)),
        'regex': regex
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(automaton_dict, f, ensure_ascii=False, indent=4)


def load_automaton_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            automaton_dict = json.load(f)

        states = set(automaton_dict['states'])
        input_symbols = set(automaton_dict['input_symbols'])
        initial_state = automaton_dict['initial_state']
        final_states = set(automaton_dict['final_states'])
        automaton_type = automaton_dict['type']
        transitions_from_json = automaton_dict['transitions']
        regex = automaton_dict.get('regex', '')

        if automaton_type == 'DFA':
            transitions = {
                str(state): {
                    symbol: str(dest)
                    for symbol, dest in state_map.items()
                }
                for state, state_map in transitions_from_json.items()
            }

            dfa = DFA(
                states=states,
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states
            )
            return dfa, regex

        else:
            transitions = {
                str(state): {
                    symbol: set(str(dest) for dest in dest_states)
                    for symbol, dest_states in state_map.items()
                }
                for state, state_map in transitions_from_json.items()
            }

            nfa = NFA(
                states=states,
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states
            )
            return nfa, regex

    except (IOError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка при загрузке или парсинге файла: {e}")
        return None, ""