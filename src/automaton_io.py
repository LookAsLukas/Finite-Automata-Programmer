import json
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


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

    # Для NFA значения переходов (dest_states) являются множествами (set) и их нужно
    # преобразовать в списки для сериализации в JSON.
    # Для DFA значения уже являются строками и не требуют преобразования.
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

    Args:
        file_path (str): Путь к JSON-файлу.

    Returns:
        Объект DFA или NFA, либо None в случае ошибки.
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
            return NFA(
                states=states,
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states
            )

    except (IOError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Ошибка при загрузке или парсинге файла: {e}")
        return None
