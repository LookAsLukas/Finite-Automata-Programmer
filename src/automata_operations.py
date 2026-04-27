from __future__ import annotations

from automata.fa.nfa import NFA
from automata_visualizer import automaton_to_graph
from application_state import EPSILON_SYMBOL, EditorMode
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
    """Конвертация с учетом весов состояний (кол-во входящих * кол-во исходящих переходов) для оптимизации порядка исключения."""
    new_start, new_final = "__S__", "__F__"
    states = sorted(nfa.states, key=str)
    all_states = [new_start, *states, new_final]
    
    trans = {(s, e): None for s in all_states for e in all_states}
    
    for s, s_trans in nfa.transitions.items():
        for symb, targets in s_trans.items():
            char = EPSILON_SYMBOL if symb == '' else symb
            for t in targets:
                trans[(s, t)] = _union_regex(trans[(s, t)], char)

    trans[(new_start, nfa.initial_state)] = EPSILON_SYMBOL
    for f in nfa.final_states:
        trans[(f, new_final)] = _union_regex(trans[(f, new_final)], EPSILON_SYMBOL)

    # Удаление по весам (In * Out)
    def get_weight(state):
        in_d = sum(1 for s in all_states if trans[(s, state)] and s != state)
        out_d = sum(1 for e in all_states if trans[(state, e)] and e != state)
        return in_d * out_d

    elimination_order = sorted(states, key=get_weight)

    for q_elim in elimination_order:
        remaining = [s for s in all_states if s != q_elim]
        loop = trans[(q_elim, q_elim)]
        
        for s in remaining:
            if not trans[(s, q_elim)]: continue
            for e in remaining:
                if not trans[(q_elim, e)]: continue
                
                path = _concat_regex(trans[(s, q_elim)], _star_regex(loop), trans[(q_elim, e)])
                trans[(s, e)] = _union_regex(trans[(s, e)], path)
        
        for s in all_states:
            trans[(s, q_elim)] = trans[(q_elim, s)] = None

    return simplify_regex(trans[(new_start, new_final)] or "∅")

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

    old_states = sorted([s for s in automaton.states if s != ""], key=str)
    state_map = {old: f"q{i}" for i, old in enumerate(old_states)}
    state_map[""] = ""

    new_states = {state_map.get(s, str(s)) for s in automaton.states}
    new_initial = state_map.get(automaton.initial_state, str(automaton.initial_state))
    new_final = {state_map.get(s, str(s)) for s in automaton.final_states}

    new_transitions = {}
    for s, trans in automaton.transitions.items():
        mapped_s = state_map.get(s, str(s))
        new_transitions[mapped_s] = {}
        for sym, targets in trans.items():
            if isinstance(targets, set) or isinstance(targets, frozenset):
                new_transitions[mapped_s][sym] = {state_map.get(t, str(t)) for t in targets}
            else: 
                new_transitions[mapped_s][sym] = {state_map.get(targets, str(targets))}

    automaton = NFA(
        states=new_states,
        input_symbols=automaton.input_symbols,
        transitions=new_transitions,
        initial_state=new_initial,
        final_states=new_final
    )

    if automaton.initial_state != "":
        automaton = NFA(
            states=automaton.states.union({""}),
            input_symbols=automaton.input_symbols,
            transitions=automaton.transitions | {"": {'': {automaton.initial_state}}},
            initial_state="",
            final_states=automaton.final_states
        )

    try:
        from edit_events import set_editor_mode

        app.history.add(app.graph)
        app.graph = automaton_to_graph(automaton, app)
        app.attr.alphabet = set(automaton.input_symbols)
        set_editor_mode(app, EditorMode.SELECT, update_page=False)

        if app.attr.alphabet:
            app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"
        else:
            app.ui.alphabet_display.value = "Алфавит: ∅"

        app.ui.status_text.value = "Автомат импортирован"

        return True
    except Exception as ex:
        app.history.remove()
        app.ui.status_text.value = f"Ошибка при импорте автомата: {ex}"
        print(ex)
        return False
