import flet as ft
from flet import Row, ElevatedButton, Container, Colors
from time import sleep
from automata_operations import build_nfa_from_ui
from draw import draw_nodes
from fap import Application


def get_epsilon_closure(nfa, states):
    """
    Находит все состояния, достижимые из текущих только по эпсилон-переходам.
    """
    closure = set(states)
    stack = list(states)
    
    while stack:
        state = stack.pop()
        if state in nfa.transitions:
            for symbol, destinations in nfa.transitions[state].items():
                if symbol == '' or symbol == 'ε':
                    for dest in destinations:
                        if dest not in closure:
                            closure.add(dest)
                            stack.append(dest)
    return closure


def toggle_debug_mode(app: Application):
    if app.attr.debug_mode:
        app.attr.debug_mode = False
        app.attr.auto_playing = False 
        app.attr.current_states.clear()
        app.ui.debug_panel.visible = False
        
        # Сбрасываем форматирование (spans) и возвращаем обычный текст
        app.ui.status_text.spans = None
        app.ui.status_text.value = "Режим отладки выключен"
        
        app.attr.debug_step_info = ""
        app.ui.debug_status_text.visible = False 
        draw_nodes(app)
        app.page.update()
    else:
        word = app.ui.word_input.value.strip()
        if not word:
            app.ui.status_text.value = "Введите слово для отладки!"
            app.page.update()
            return
            
        nfa = build_nfa_from_ui(app)
        if not nfa:
            app.ui.status_text.value = "Автомат не построен!"
            app.page.update()
            return
            
        app.attr.debug_mode = True
        app.attr.auto_playing = False 
        app.attr.input_string = word
        app.attr.input_position = 0
        
        start_states = {node.name for node in app.graph.get_start_states()}
        app.attr.current_states = get_epsilon_closure(nfa, start_states)
        
        app.ui.debug_panel.visible = True
        app.ui.debug_status_text.visible = True
        
        update_debug_view(app, "Начало работы")


def debug_step_forward(app: Application, is_auto: bool = False):
    if not app.attr.debug_mode:
        return
    
    if getattr(app.attr, 'auto_playing', False) and not is_auto:
        return
    
    if app.attr.input_position >= len(app.attr.input_string):
        check_acceptance(app)
        return

    nfa = build_nfa_from_ui(app)
    if not nfa:
        return

    current_char = app.attr.input_string[app.attr.input_position]
    
    next_states_direct = set()
    
    current_closure = get_epsilon_closure(nfa, app.attr.current_states)
    
    for state in current_closure:
        if state in nfa.transitions:
            if current_char in nfa.transitions[state]:
                next_states_direct.update(nfa.transitions[state][current_char])
    
    if not next_states_direct:
        app.attr.current_states = set()
        app.attr.input_position += 1
        update_debug_view(app, f"Символ '{current_char}': переходов нет")
        return

    next_states_closure = get_epsilon_closure(nfa, next_states_direct)
    
    app.attr.current_states = next_states_closure
    app.attr.input_position += 1
    
    update_debug_view(app, f"Символ '{current_char}' обработан")


def debug_step_back(app: Application):
    if not app.attr.debug_mode:
        return
        
    if getattr(app.attr, 'auto_playing', False):
        return
    
    if app.attr.input_position <= 0:
        return
    
    app.attr.input_position -= 1
    
    nfa = build_nfa_from_ui(app)
    if not nfa:
        return
        
    start_states = {node.name for node in app.graph.get_start_states()}
    app.attr.current_states = get_epsilon_closure(nfa, start_states)
    
    target_pos = app.attr.input_position
    for i in range(target_pos):
        char = app.attr.input_string[i]
        
        next_direct = set()
        current_closure = get_epsilon_closure(nfa, app.attr.current_states)
        
        for state in current_closure:
            if state in nfa.transitions and char in nfa.transitions[state]:
                next_direct.update(nfa.transitions[state][char])
        
        app.attr.current_states = get_epsilon_closure(nfa, next_direct)

    prev_char = app.attr.input_string[target_pos - 1] if target_pos > 0 else "START"
    msg = f"Откат назад. Перед символом '{app.attr.input_string[target_pos]}'" if target_pos < len(app.attr.input_string) else "Откат с конца"
    update_debug_view(app, msg)


def debug_continue(app: Application):

    if not app.attr.debug_mode:
        return
        
    if getattr(app.attr, 'auto_playing', False) or app.attr.input_position >= len(app.attr.input_string):
        return
        
    app.attr.auto_playing = True
    
    try:
        while app.attr.input_position < len(app.attr.input_string):
            sleep(1)
            if not app.attr.debug_mode:
                break
                
            debug_step_forward(app, is_auto=True)
            
        if app.attr.debug_mode and app.attr.input_position >= len(app.attr.input_string):
            sleep(1)
            if app.attr.debug_mode:
                check_acceptance(app)
                
    finally:
        app.attr.auto_playing = False


def update_debug_view(app: Application, message: str):
    states_str = ', '.join(sorted([str(s) for s in app.attr.current_states if s != ""]))
    if not states_str:
        states_str = "∅ (тупик)"
        
    pos = app.attr.input_position
    total = len(app.attr.input_string)
    word = app.attr.input_string
    
    step_info = f"Шаг {pos}/{total}. {message}. Состояния: {{{states_str}}}"
    
    spans = []
    
    if pos > 0:
        spans.append(ft.TextSpan(word[:pos], style=ft.TextStyle(size=18)))
        
    if pos < total:
        spans.append(ft.TextSpan(word[pos], style=ft.TextStyle(color=Colors.RED, weight="bold", size=18)))
        
    if pos + 1 < total:
        spans.append(ft.TextSpan(word[pos+1:], style=ft.TextStyle(size=18)))

    app.ui.status_text.value = "" 
    app.ui.status_text.spans = spans

    if pos == total:
        final_states = {node.name for node in app.graph.get_final_states()}
        is_accepted = any(s in final_states for s in app.attr.current_states)
        
        if is_accepted:
            step_info += " -> ✅ СЛОВО ПРИНЯТО"
            spans.append(ft.TextSpan(" ✅", style=ft.TextStyle(size=18)))
        else:
            step_info += " -> ❌ СЛОВО ОТВЕРГНУТО"
            spans.append(ft.TextSpan(" ❌", style=ft.TextStyle(size=18)))

    app.attr.debug_step_info = step_info
    app.ui.debug_status_text.value = step_info
    
    draw_nodes(app)
    app.page.update()


def check_acceptance(app: Application):
    """Вызывается если нажали 'Вперед' в конце слова"""
    final_states = {node.name for node in app.graph.get_final_states()}
    is_accepted = any(s in final_states for s in app.attr.current_states)
    
    result_text = "Слово принято!" if is_accepted else "Слово не принято (нет финальных состояний)"
    dialog = ft.AlertDialog(
        title=ft.Text("Результат"),
        content=ft.Text(result_text),
        actions=[ft.ElevatedButton("OK", on_click=lambda e: app.page.close(dialog))]
    )
    app.page.open(dialog)
    app.page.update()