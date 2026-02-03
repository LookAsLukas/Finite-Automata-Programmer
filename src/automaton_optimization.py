from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from automata_operations import import_automaton_data, build_nfa_from_ui
from draw import draw_nodes
from fap import Application


def handle_optimize_click(app: Application):
    if app.graph.get_start_states() == set():
        app.ui.status_text.value = "Ошибка: выберите хотя бы одно начальное состояние!" # TODO: MAKE MORE AGGRESSIVE
        app.page.update()
        return

    app.ui.status_text.value = "Оптимизация..."
    app.page.update()

    try:
        nfa = build_nfa_from_ui(app)
        if nfa is None:
            app.ui.status_text.value = "Ошибка построения NFA (проверьте граф)"
            app.page.update()
            return

        min_nfa = NFA.from_dfa(DFA.from_nfa(nfa).minify())
        if import_automaton_data(min_nfa, app):
            draw_nodes(app)
            app.ui.status_text.value = "Оптимизация выполнена успешно!"
        else:
            app.ui.status_text.value = "Ошибка отрисовки результата"
    except Exception as ex:
        error_msg = str(ex)
        if "frozendict" in error_msg:
            error_msg = "Внутренняя ошибка библиотеки (frozendict)"
        app.ui.status_text.value = f"Сбой: {error_msg}"
        print(f"FULL ERROR: {ex}")

    app.page.update()
