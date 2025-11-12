from automata.fa.nfa import NFA
from automata_io import save_automaton_to_json, load_automaton_from_json
from automata_visualizer import prepare_automaton_layout
from draw import draw_nodes


def build_nfa_from_ui(attr):
    """Создает объект NFA из automata-lib на основе текущего автомата"""
    if not attr.nodes or attr.start_state is None:
        return None

    states = set(attr.nodes.keys())
    initial_state = attr.start_state
    final_state_names = attr.final_states

    nfa_transitions = {}
    for start_name, trans_list in attr.transitions.items():
        nfa_transitions[start_name] = {}
        for t in trans_list:
            symbol = t["symbol"]
            end_name = t["end"]
            nfa_transitions[start_name].setdefault(symbol, set()).add(end_name)

    for name in states:
        nfa_transitions.setdefault(name, {})

    return NFA(
        states=states,
        input_symbols=set(attr.alphabet),
        transitions=nfa_transitions,
        initial_state=initial_state,
        final_states=final_state_names,
    )


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
        save_automaton_to_json(nfa, export_path)
        ui.status_text.value = f"✅ NFA экспортирован в файл {export_path}"
    except (TypeError, IOError) as err:
        ui.status_text.value = f"Ошибка экспорта: {err}"
    page.update()


def import_automaton(e, attr, ui, page):
    """Импорт автомата из JSON файла"""
    automaton = load_automaton_from_json("nfa.json")
    if automaton is None:
        ui.status_text.value = "Не удалось загрузить автомат из nfa.json"
        page.update()
        return

    try:
        layout = prepare_automaton_layout(automaton, canvas_width=700, canvas_height=450)
        layout_nodes, layout_state_names, layout_transitions, layout_final_states, layout_start_index, layout_alphabet = layout

        # Конвертируем формат данных из automata_visualizer в наш формат
        attr.nodes = {}
        for i, (x, y) in enumerate(layout_nodes):
            attr.nodes[layout_state_names[i]] = (x, y)
        
        attr.transitions = {}
        for start_idx, trans_list in layout_transitions.items():
            start_name = layout_state_names[start_idx]
            attr.transitions[start_name] = []
            for t in trans_list:
                end_name = layout_state_names[t["end"]]
                attr.transitions[start_name].append({"symbol": t["symbol"], "end": end_name})
        
        attr.final_states = {layout_state_names[i] for i in layout_final_states}
        attr.start_state = layout_state_names[layout_start_index] if layout_start_index is not None else None
        attr.alphabet = set(layout_alphabet)
        attr.node_counter = len(layout_state_names)
        attr.placing_mode = False
        attr.transition_mode = False
        attr.selected_node = None
        attr.first_selected_node = None

        ui.alphabet_display.value = f"Алфавит: {', '.join(sorted(attr.alphabet))}" if attr.alphabet else "Алфавит: ∅"
        ui.mode_status.value = "Режим размещения: выключен"
        ui.transition_status.value = "Режим переходов: выключен"
        ui.status_text.value = "✅ Автомат импортирован из nfa.json"

        draw_nodes(attr, ui)
        page.update()
        
    except Exception as ex:
        ui.status_text.value = f"Ошибка при импорте автомата: {ex}"
        page.update()


