from automata_operations import build_nfa_from_ui, import_automaton_data
from automata_io import load_automaton_from_json, save_automaton_to_json
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


def _validate_automaton_before_export(attr):
    """Проверяет, что автомат заполнен перед экспортом."""
    if not attr.nodes:
        return "Автомат пуст — нечего экспортировать!"
    if not attr.final_states:
        return "Добавьте хотя бы одно конечное состояние!"
    if not attr.alphabet:
        return "Алфавит пуст — добавьте символы!"
    if attr.start_state is None:
        return "Не выбрано начальное состояние!"
    if attr.start_state not in attr.transitions or not attr.transitions.get(attr.start_state):
        return "Начальное состояние должно иметь хотя бы один исходящий переход!"
    return None


def export_nfa_to_path(export_path, attr, ui, page):
    """Экспорт автомата в JSON файл по указанному пути."""
    error_message = _validate_automaton_before_export(attr)
    if error_message:
        ui.status_text.value = error_message
        page.update()
        return

    try:
        nfa = build_nfa_from_ui(attr)
        if nfa is None:
            ui.status_text.value = "Автомат неполный — экспорт невозможен!"
            page.update()
            return
        save_automaton_to_json(nfa, export_path)
        ui.status_text.value = f"✅ NFA экспортирован в файл {export_path}"
    except Exception as err:
        ui.status_text.value = f"Ошибка экспорта: {err}"
    page.update()


def import_automaton_from_path(file_path, attr, ui, page):
    """Импорт автомата из JSON файла по указанному пути."""
    automaton = load_automaton_from_json(file_path)
    if automaton is None:
        ui.status_text.value = f"Не удалось загрузить автомат из {file_path}"
        page.update()
        return

    if import_automaton_data(automaton, attr, ui):
        draw_nodes(attr, ui)
        page.update()


def request_file_open(e, attr, ui, page):
    """Открывает диалог выбора файла для импорта автомата."""
    if ui.open_file_picker:
        ui.open_file_picker.pick_files(allow_multiple=False, allowed_extensions=["json"])
    else:
        ui.status_text.value = "Диалог выбора файла недоступен"
        page.update()


def handle_open_file_result(e, attr, ui, page):
    """Обрабатывает выбранный в диалоге файл импорта."""
    if not e.files:
        ui.status_text.value = "Выбор файла отменен"
        page.update()
        return

    file_path = e.files[0].path
    import_automaton_from_path(file_path, attr, ui, page)


def request_file_save(e, attr, ui, page):
    """Открывает диалог сохранения автомата в файл."""
    error_message = _validate_automaton_before_export(attr)
    if error_message:
        ui.status_text.value = error_message
        page.update()
        return

    if ui.save_file_picker:
        ui.save_file_picker.save_file(file_name="nfa.json", allowed_extensions=["json"])
    else:
        ui.status_text.value = "Диалог сохранения недоступен"
        page.update()


def handle_save_file_result(e, attr, ui, page):
    """Обрабатывает выбранный путь для сохранения автомата."""
    if not e.path:
        ui.status_text.value = "Сохранение отменено"
        page.update()
        return

    export_nfa_to_path(e.path, attr, ui, page)
