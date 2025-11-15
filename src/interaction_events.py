from automata_operations import build_nfa_from_ui, import_automaton_data
from automata_io import load_automaton_from_json
from draw import draw_nodes


def handle_run(e, attr, ui, page):
    """Обработка слова с использованием automata-lib"""
    if attr.start_state is None:
        ui.status_text.value = "Не выбрано начальное состояние!"
        page.update()
        return
    
    nfa = build_nfa_from_ui(attr)
    if nfa is None:
        ui.status_text.value = "Автомат неполный — добавьте состояния!"
        page.update()
        return
    
    word = ui.word_input.value.strip()
    if not word:
        ui.status_text.value = "Введите слово!"
    else:
        try:
            accepted = nfa.accepts_input(word)
            ui.status_text.value = f"Слово '{word}' {'✅ принимается' if accepted else '❌ не принимается'} автоматом"
        except Exception as ex:
            ui.status_text.value = f"Ошибка при обработке слова: {ex}"
    page.update()


def export_nfa(e, attr, ui, page):
    """Экспорт автомата в JSON файл"""
    if not attr.nodes:
        ui.status_text.value = "Автомат пуст — нечего экспортировать!"
        page.update()
        return

    if not attr.final_states:
        ui.status_text.value = "Добавьте хотя бы одно конечное состояние!"
        page.update()
        return

    if not attr.alphabet:
        ui.status_text.value = "Алфавит пуст — добавьте символы!"
        page.update()
        return

    if attr.start_state is None:
        ui.status_text.value = "Не выбрано начальное состояние!"
        page.update()
        return

    try:
        nfa = build_nfa_from_ui(attr)
        if nfa is None:
            ui.status_text.value = "Автомат неполный — экспорт невозможен!"
            page.update()
            return
        export_path = "nfa.json"
        from automata_io import save_automaton_to_json
        save_automaton_to_json(nfa, export_path)
        ui.status_text.value = f"✅ NFA экспортирован в файл {export_path}"
    except Exception as err:
        ui.status_text.value = f"Ошибка экспорта: {err}"
    page.update()


def import_automaton(e, attr, ui, page):
    """Импорт автомата из JSON файла"""
    automaton = load_automaton_from_json("nfa.json")
    if automaton is None:
        ui.status_text.value = "Не удалось загрузить автомат из nfa.json"
        page.update()
        return

    if import_automaton_data(automaton, attr, ui):
        draw_nodes(attr, ui)
        page.update()