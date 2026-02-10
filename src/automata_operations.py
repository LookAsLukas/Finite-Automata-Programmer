from automata.fa.nfa import NFA
from automata_visualizer import automaton_to_graph
from application_state import EPSILON_SYMBOL
from fap import Application


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