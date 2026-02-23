from automata.fa.nfa import NFA
from automata_visualizer import automaton_to_graph
from application_state import EPSILON_SYMBOL
from fap import Application
import re

EMPTY_SET_SYMBOL = "∅"

def _is_wrapped(regex: str) -> bool:
    if not regex.startswith("(") or not regex.endswith(")"):
        return False

    depth = 0
    for ind, char in enumerate(regex):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1

        if depth == 0 and ind != len(regex) - 1:
            return False

    return depth == 0


def _wrap_if_needed(regex: str) -> str:
    if len(regex) <= 1:
        return regex

    if _is_wrapped(regex):
        return regex

    return f"({regex})"


def _union_regex(left: str | None, right: str | None) -> str | None:
    if left is None:
        return right
    if right is None:
        return left
    if left == right:
        return left
    return f"{left}|{right}"


def _concat_regex(*parts: str | None) -> str | None:
    filtered_parts = [part for part in parts if part not in (None, EPSILON_SYMBOL)]

    if any(part is None for part in parts):
        return None
    if not filtered_parts:
        return EPSILON_SYMBOL

    return ''.join(_wrap_if_needed(part) for part in filtered_parts)


def _star_regex(regex: str | None) -> str:
    if regex is None or regex == EPSILON_SYMBOL:
        return EPSILON_SYMBOL
    if len(regex) == 1:
        return f"{regex}*"
    if regex.endswith("*") and _is_wrapped(regex[:-1]):
        return regex
    return f"{_wrap_if_needed(regex)}*"


def nfa_to_regex_state_elimination(nfa: NFA) -> str:
    """Преобразует NFA в регулярное выражение методом исключения состояний."""
    new_start = "__GNFA_START__"
    new_final = "__GNFA_FINAL__"

    states = sorted(nfa.states, key=str)
    all_states = [new_start, *states, new_final]
    transitions: dict[tuple[str, str], str | None] = {
        (start, end): None
        for start in all_states
        for end in all_states
    }

    for start, state_transitions in nfa.transitions.items():
        for symbol, destinations in state_transitions.items():
            regex_symbol = EPSILON_SYMBOL if symbol == '' else symbol
            for end in destinations:
                transitions[(start, end)] = _union_regex(transitions[(start, end)], regex_symbol)

    transitions[(new_start, nfa.initial_state)] = _union_regex(
        transitions[(new_start, nfa.initial_state)],
        EPSILON_SYMBOL,
    )
    for final_state in nfa.final_states:
        transitions[(final_state, new_final)] = _union_regex(
            transitions[(final_state, new_final)],
            EPSILON_SYMBOL,
        )

    elimination_order = sorted(nfa.states, key=str)
    for eliminated_state in elimination_order:
        remaining_states = [state for state in all_states if state != eliminated_state]
        loop = transitions[(eliminated_state, eliminated_state)]

        for start in remaining_states:
            for end in remaining_states:
                through_eliminated = _concat_regex(
                    transitions[(start, eliminated_state)],
                    _star_regex(loop),
                    transitions[(eliminated_state, end)],
                )
                transitions[(start, end)] = _union_regex(
                    transitions[(start, end)],
                    through_eliminated,
                )

        for state in all_states:
            transitions[(state, eliminated_state)] = None
            transitions[(eliminated_state, state)] = None

    result = transitions[(new_start, new_final)] or EMPTY_SET_SYMBOL
    return simplify_regex(result)

def simplify_regex(regex: str) -> str:
    if regex in (None, "∅", "ε"):
        return regex

    # Защита от зацикливания – применяем правила, пока выражение меняется
    prev = None
    while prev != regex:
        prev = regex

        # 1. (a) -> a
        regex = re.sub(r'\(([a-zA-Z0-9ε])\)', r'\1', regex)

        # 2. ε* -> ε
        regex = re.sub(r'ε\*', 'ε', regex)

        # 3. (expr)* где expr уже содержит * -> убираем внешнюю звезду (например (a*)* -> a*)
        def unwrap_star(match):
            inner = match.group(1)
            return inner if inner.endswith('*') else match.group(0)
        regex = re.sub(r'\(([^()]+)\)\*', unwrap_star, regex)

        # 4. ∅|a -> a, a|∅ -> a
        regex = re.sub(r'∅\|([^()|]+)', r'\1', regex)
        regex = re.sub(r'([^()|]+)\|∅', r'\1', regex)

        # 5. aε -> a, εa -> a
        regex = re.sub(r'([^()|ε])ε|ε([^()|ε])', r'\1\2', regex)

        # 6. ((a)) -> (a) -> a 
        while re.search(r'\(\([^()]+\)\)', regex):
            regex = re.sub(r'\(\(([^()]+)\)\)', r'(\1)', regex)

        # 7. (ε|X*) -> X*  и  ε|X* -> X*
        pattern2 = r'(?:\(ε\|([^()|]+)\*\)|ε\|([^()|]+)\*)'
        def replace2(match):
            group = match.group(1) or match.group(2)
            return f"{group}*"
        regex = re.sub(pattern2, replace2, regex)

        # 8. (ε|X(X*)) -> X* 
        pattern1 = r'(?:\(ε\|([^()|*]+)\(\1\*\)\)|ε\|([^()|*]+)\(\2\*\))'
        def replace1(match):
            group = match.group(1) or match.group(2)
            return f"{group}*"
        regex = re.sub(pattern1, replace1, regex)

        # 9. X|X -> X 
        def dedup_alt(match):
            a = match.group(1)
            b = match.group(2)
            return a if a == b else match.group(0)
        regex = re.sub(r'\(([^()|]+)\|([^()|]+)\)', dedup_alt, regex)

        # 10. (X)Y -> XY, X(Y) -> XY
        regex = re.sub(r'\(([^()|*]+)\)([^()|*])', r'\1\2', regex)  # (X)Y
        regex = re.sub(r'([^()|*])\(([^()|*]+)\)', r'\1\2', regex)  # X(Y)

        # 11. X** -> X* 
        regex = re.sub(r'([^()|*]+)\*\*', r'\1*', regex)
    return regex

def build_nfa_from_ui(app: Application) -> NFA:
    """
    Создает объект NFA.
    Исправлено: теперь корректно обрабатывает переходы, даже если объекты узлов
    в transition не совпадают по ссылке с объектами в app.graph.nodes.
    """
    if app.graph.nodes == set() or app.graph.get_start_states() == set():
        return None

    nfa_transitions = {}
    
    for node in app.graph.nodes:
        nfa_transitions[node.name] = {}
    
    for transition in app.graph.transitions:
        
        start_name = transition.start.name
        end_name = transition.end.name

        if start_name not in nfa_transitions:
            continue

        for symbol in transition.symbols:
            if symbol == EPSILON_SYMBOL:
                symbol = ''
            
            nfa_transitions[start_name].setdefault(symbol, set()).add(end_name)

    nfa_transitions[""] = {
        '': set(map(lambda node: node.name, app.graph.get_start_states()))
    }

    try:
        return NFA(
            states=set(map(lambda node: node.name, app.graph.nodes)) | {""},
            input_symbols=app.attr.alphabet,
            transitions=nfa_transitions,
            initial_state="",
            final_states=set(map(lambda node: node.name, app.graph.get_final_states())),
        )
    except Exception as e:
        print(f"Ошибка создания NFA: {e}")
        return None


def import_automaton_data(automaton: NFA, app: Application) -> bool:
    """
    Импортирует данные из объекта DFA/NFA (automata-lib) в атрибуты приложения.
    """

    if automaton.initial_state != "":
        automaton = NFA(
            states=automaton.states.union({""}),
            input_symbols=automaton.input_symbols,
            transitions=automaton.transitions | {"": {'': {automaton.initial_state}}},
            initial_state="",
            final_states=automaton.final_states
        )

    try:
        app.graph = automaton_to_graph(automaton, app)
        app.attr.alphabet = automaton.input_symbols
        app.attr.placing_mode = False
        app.attr.transition_mode = False

        if app.attr.alphabet:
            app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"
        else:
            app.ui.alphabet_display.value = "Алфавит: ∅"
            
        app.ui.mode_status.value = "Mode: Normal"
        app.ui.status_text.value = "Автомат импортирован"

        return True
    except Exception as ex:
        app.ui.status_text.value = f"Ошибка при импорте автомата: {ex}"
        print(ex)
        return False