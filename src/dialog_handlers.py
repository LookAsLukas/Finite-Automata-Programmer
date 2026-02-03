from flet import Text, TextField, ElevatedButton, AlertDialog, Row, MainAxisAlignment
from automata_operations import import_automaton_data
from automata.fa.nfa import NFA
from application_state import EPSILON_SYMBOL
from draw import draw_nodes
from graph import Node, Transition
from fap import Application


def rename_state_dialog(node: Node, app: Application) -> AlertDialog:
    """Создает диалог для переименования состояния."""
    def on_submit(e):
        new_name = input_field.value.strip()
        if new_name == "" or new_name in map(lambda node: node.name, app.graph.nodes):
            app.ui.status_text.value = "Некорректное или занятое имя!" # TODO: MAKE MORE AGRESSIVE
            app.page.close(dialog)
            app.page.update()
            return

        node.name = new_name

        draw_nodes(app)
        app.page.close(dialog)
        app.page.update()

    input_field = TextField(label="Новое имя", value=node.name, autofocus=True, on_submit=on_submit)
    dialog = AlertDialog(
        title=Text(f"Переименовать {node.name}"),
        content=input_field,
        actions=[ElevatedButton("OK", on_click=on_submit)]
    )
    return dialog


def edit_transition_dialog(transition: Transition, app: Application) -> AlertDialog:
    def on_save(e):
        new_symbols = set(input_field.value.strip())
        if new_symbols == set():
            app.ui.status_text.value = "Символ не может быть пустым (используйте ε)!" # TODO: MAKE MORE AGGRESSIVE
            return

        transition.symbols = ''.join(new_symbols)

        if new_symbols != {EPSILON_SYMBOL}:
            app.attr.alphabet.update(new_symbols)
            app.ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(app.attr.alphabet))}"

        draw_nodes(app)
        app.page.close(dialog)
        app.page.update()

    def set_epsilon(e):
        input_field.value += EPSILON_SYMBOL
        input_field.focus()
        app.page.update()

    input_field = TextField(
        label="Символы перехода",
        value=transition.symbols,
        width=150,
        autofocus=True,
        on_submit=on_save
    )

    epsilon_btn = ElevatedButton(
        text=EPSILON_SYMBOL,
        on_click=set_epsilon,
        tooltip="Добавить эпсилон к символам перехода"
    )

    content_row = Row(
        controls=[input_field, epsilon_btn],
        vertical_alignment="center",
        alignment=MainAxisAlignment.START
    )

    dialog = AlertDialog(
        title=Text(f"Изменить переход {transition.start.name} -> {transition.end.name}"),
        content=content_row,
        actions=[
            ElevatedButton("Сохранить", on_click=on_save)
        ],
    )
    return dialog


def regex_input_dialog(app: Application) -> AlertDialog:
    def on_build(e):
        regex_str = input_field.value.strip()
        if regex_str == "":
            return

        app.page.close(dialog)

        try:
            nfa = NFA.from_regex(regex_str)
        except Exception as ex:
            error_dialog = AlertDialog(
                modal=True,
                title=Text("Ошибка синтаксиса"),
                content=Text(f"Регулярное выражение '{regex_str}' содержит ошибки.\n{ex}"),
                actions=[
                    ElevatedButton("OK", on_click=lambda e: app.page.close(error_dialog)),
                ],
            )
            app.page.open(error_dialog)
        else:
            app.attr.regex = regex_str
            app.ui.regex_display.value = f"Регулярное выражение: {regex_str}"

            if import_automaton_data(nfa, app):
                draw_nodes(app)
                app.ui.debug_panel.visible = False
                app.ui.status_text.value = f"✅ Автомат построен из: {regex_str}"
            else:
                app.ui.status_text.value = "❌ Ошибка при построении"

        app.page.update()

    input_field = TextField(
        label="Регулярное выражение",
        hint_text="Пример: (a|b)*abb",
        autofocus=True,
        width=400,
        on_submit=on_build
    )
    dialog = AlertDialog(
        modal=True,
        title=Text("Построение автомата из регулярного выражения"),
        content=input_field,
        actions=[
            ElevatedButton("Отмена", on_click=lambda e: app.page.close(dialog)),
            ElevatedButton("Построить", on_click=on_build),
        ],
        actions_alignment=MainAxisAlignment.END,
    )
    return dialog
