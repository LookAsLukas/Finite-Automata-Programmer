import os

from automata_operations import build_nfa_from_ui, import_automaton_data
from automata_io import load_automaton_from_json, save_automaton_to_json
from draw import draw_nodes
from fap import Application
from flet import FilePicker


def handle_run(app: Application) -> None:
    """Обработка слова с использованием automata-lib"""
    if app.graph.get_start_states() == set():
        app.ui.status_text.value = "Выберите хотя бы одно начальное сотояние"
        app.page.update()
        return

    nfa = build_nfa_from_ui(app)
    if nfa is None:
        app.ui.status_text.value = "Автомат неполный — добавьте состояния!"
        app.page.update()
        return

    word = app.ui.word_input.value.strip()
    if not word:
        app.ui.status_text.value = "Введите слово!"
    else:
        try:
            accepted = nfa.accepts_input(word)
            app.ui.status_text.value = f"Слово '{word}' {'✅ принимается' if accepted else '❌ не принимается'} автоматом"
        except Exception as ex:
            app.ui.status_text.value = f"Ошибка при обработке слова: {ex}"
    app.page.update()


def _get_automaton_export_error(app: Application) -> str | None:
    """Проверяет, что автомат заполнен перед экспортом."""
    if app.graph.get_start_states() == set():
        return "Добавьте хотя бы одно начальное состояние!"
    if app.graph.get_final_states() == set():
        return "Добавьте хотя бы одно конечное состояние!"
    if app.attr.alphabet == set():
        return "Алфавит пуст — добавьте символы!"
    return None


def _ensure_json_extension(file_path) -> str:
    """Гарантирует, что экспорт сохраняется в файл .json."""
    base, ext = os.path.splitext(file_path)
    if ext.lower() != ".json":
        return f"{base}.json"
    return file_path


def export_nfa_to_path(export_path: str, app: Application) -> None:
    """Экспорт автомата в JSON файл по указанному пути."""
    error_message = _get_automaton_export_error(app)
    if error_message:
        app.ui.status_text.value = error_message
        app.page.update()
        return

    export_path = _ensure_json_extension(export_path)
    try:
        nfa = build_nfa_from_ui(app)
        if nfa is None:
            app.ui.status_text.value = "Автомат неполный — экспорт невозможен!"
            app.page.update()
            return
        save_automaton_to_json(nfa, export_path, app.attr.regex)
        app.ui.status_text.value = f"✅ NFA экспортирован в файл {export_path}"
    except Exception as err:
        app.ui.status_text.value = f"Ошибка экспорта: {err}"
    app.page.update()


def import_automaton_from_path(file_path: str, app: Application) -> None:
    automaton, regex = load_automaton_from_json(file_path)
    if automaton is None:
        app.ui.status_text.value = f"Не удалось загрузить автомат из {file_path}"
        app.page.update()
        return

    if import_automaton_data(automaton, app):
        if regex:
            app.attr.regex = regex
            app.ui.regex_display.value = f"Регулярное выражение: {regex}"
        draw_nodes(app)
        app.page.update()


def request_file_open(app: Application) -> None:
    """Открывает диалог выбора файла для импорта автомата."""
    app.ui.open_file_picker.pick_files(allow_multiple=False, allowed_extensions=["json"])


def handle_open_file_result(e, app: Application) -> None:
    """Обрабатывает выбранный в диалоге файл импорта."""
    if not e.files:
        app.ui.status_text.value = "Выбор файла отменен"
        app.page.update()
        return

    file_path = e.files[0].path
    import_automaton_from_path(file_path, app)


def request_file_save(app: Application) -> None:
    """Открывает диалог сохранения автомата в файл."""
    error_message = _get_automaton_export_error(app)
    if error_message:
        app.ui.status_text.value = error_message
        app.page.update()
        return

    app.ui.save_file_picker.save_file(file_name="nfa.json", allowed_extensions=["json"])


def handle_save_file_result(e, app: Application) -> None:
    """Обрабатывает выбранный путь для сохранения автомата."""
    if not e.path:
        app.ui.status_text.value = "Сохранение отменено"
        app.page.update()
        return

    export_nfa_to_path(e.path, app)
