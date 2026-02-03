import flet as ft
from flet import Row, ElevatedButton, Container, Colors
from time import sleep
from automata_operations import build_nfa_from_ui
from draw import draw_nodes
from fap import Application

def toggle_debug_mode(app: Application):

    if app.attr.debug_mode:
        app.attr.debug_mode = False
        app.attr.current_states.clear()
        app.ui.debug_panel.visible = False
        app.ui.status_text.value = "Режим отладки выключен"
        app.attr.debug_step_info = ""
        app.ui.debug_status_text.visible = False 

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
        app.attr.input_string = word
        app.attr.input_position = 0
        app.attr.current_states = {""}  
        
        app.ui.debug_panel.visible = True
        app.ui.debug_status_text.visible = True 
        app.ui.status_text.value = f"Отладка: '{word}'"
        
        start_states = app.graph.get_start_states()
        app.attr.current_states = {node.name for node in start_states}

        states_str = ', '.join(str(state) for state in app.attr.current_states)
        app.attr.debug_step_info = f"Шаг 0/{len(app.attr.input_string)}: Начальные состояния: {states_str}"
        app.ui.debug_status_text.value = app.attr.debug_step_info
    
    draw_nodes(app)
    app.page.update()


def debug_step_forward(app: Application):
    if not app.attr.debug_mode:
        return
        
    if app.attr.input_position >= len(app.attr.input_string):

        end_debug_mode(app, True)
        return
    
    current_char = app.attr.input_string[app.attr.input_position]
    app.attr.input_position += 1
    
    nfa = build_nfa_from_ui(app)
    if not nfa:
        return
        
    next_states = set()
    for state in app.attr.current_states:
        if state in nfa.transitions:
            for symbol, destinations in nfa.transitions[state].items():
                if symbol == current_char or symbol == '' or symbol == "ε":
                    next_states.update(destinations)
    
    if not next_states:
        # Нет переходов
        end_debug_mode(app, False)
        return
        
    app.attr.current_states = next_states
    
    final_states = {node.name for node in app.graph.get_final_states()}
    reached_final_states = app.attr.current_states.intersection(final_states)
    
    states_str = ', '.join(str(state) for state in sorted(app.attr.current_states))
    step_info = f"Шаг {app.attr.input_position}/{len(app.attr.input_string)}: "
    step_info += f"Символ: '{current_char}' → "
    step_info += f"Состояния: {states_str}"
    
    if reached_final_states:
        final_str = ', '.join(str(state) for state in sorted(reached_final_states))
        step_info += f" | Финальные состояния: {final_str}"
    
    app.attr.debug_step_info = step_info
    app.ui.debug_status_text.value = step_info
    
    if app.attr.current_states.intersection(final_states):
        if app.attr.input_position == len(app.attr.input_string):
            end_debug_mode(app, True)
        else:
            app.ui.status_text.value = f"Шаг {app.attr.input_position}: достигнуто финальное состояние"
    
    draw_nodes(app)
    app.page.update()

def end_debug_mode(app: Application, accepted: bool):
    """Завершение режима отладки"""
    app.attr.debug_mode = False
    app.ui.debug_panel.visible = False
    
    if accepted:
        dialog = ft.AlertDialog(
            title=ft.Text("Результат отладки"),
            content=ft.Text(f"Слово '{app.attr.input_string}' ПРИНЯТО автоматом!"),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: app.page.close(dialog))]
        )
    else:
        dialog = ft.AlertDialog(
            title=ft.Text("Результат отладки"),
            content=ft.Text(f"Слово '{app.attr.input_string}' НЕ ПРИНЯТО автоматом!"),
            actions=[ft.ElevatedButton("OK", on_click=lambda e: app.page.close(dialog))]
        )
    
    app.page.open(dialog)
    app.page.update()

def debug_step_back(app: Application):
    # Функция шага назад не реализована
    pass

def debug_continue(app: Application):
    pass