import json
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from automata.base.exceptions import MissingStateError 

def save_automaton_to_json(automaton, file_path):
    """
    Сохраняет объект конечного автомата (DFA или NFA) в файл JSON.
    Args:
        automaton: Объект DFA или NFA из библиотеки automata-lib.
        file_path (str): Путь к файлу для сохранения.
    Raises:
        TypeError: Если переданный объект не является DFA или NFA.
        IOError: Если возникает ошибка при записи файла.
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
        'states': list(automaton.states),
        'input_symbols': list(automaton.input_symbols),
        'transitions': transitions_for_json,
        'initial_state': automaton.initial_state,
        'final_states': list(automaton.final_states)
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(automaton_dict, f, ensure_ascii=False, indent=4)
        print(f"Автомат успешно сохранен в {file_path}")
    except IOError as e:
        print(f"Ошибка при сохранении файла: {e}")
        raise


def load_automaton_from_json(file_path):
    """
    Загружает конечный автомат (DFA или NFA) из файла JSON.
    Если возникает MissingStateError (начальное состояние без переходов),
    добавляем фиктивный epsilon self-loop (с символом '') для прохождения валидации.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            automaton_dict = json.load(f)

        states = set(automaton_dict['states'])
        input_symbols = set(automaton_dict['input_symbols'])
        initial_state = automaton_dict['initial_state']
        final_states = set(automaton_dict['final_states'])
        automaton_type = automaton_dict['type']
        transitions_from_json = automaton_dict['transitions']

        if automaton_type == 'DFA':
            return DFA(
                states=states,
                input_symbols=input_symbols,
                transitions=transitions_from_json,
                initial_state=initial_state,
                final_states=final_states
            )
        else:
            transitions = {
                state: {
                    symbol: set(dest_states)
                    for symbol, dest_states in transition_map.items()
                }
                for state, transition_map in transitions_from_json.items()
            }
            try:
                return NFA(
                    states=states,
                    input_symbols=input_symbols,
                    transitions=transitions,
                    initial_state=initial_state,
                    final_states=final_states
                )
            except MissingStateError:
                print(f"Автомат имел проблему с валидацией: initial state {initial_state} has no transitions defined. Добавляем фиктивный epsilon-переход для начального состояния.")
                if initial_state not in transitions:
                    transitions[initial_state] = {}
                if not transitions[initial_state]:
                    transitions[initial_state][''] = {initial_state}
                return NFA(
                    states=states,
                    input_symbols=input_symbols,
                    transitions=transitions,
                    initial_state=initial_state,
                    final_states=final_states
                )

    except (IOError, json.JSONDecodeError, KeyError, TypeError, MissingStateError) as e:
        print(f"Ошибка при загрузке или парсинге файла: {e}")
        return None