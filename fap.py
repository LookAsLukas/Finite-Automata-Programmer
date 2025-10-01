import flet as ft
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from typing import Dict, List, Tuple, Optional
import math

class State:
    def __init__(self, id: int, x: float, y: float, is_start: bool = False, is_final: bool = False):
        self.id = id
        self.x = x
        self.y = y
        self.is_start = is_start
        self.is_final = is_final
        self.radius = 25

class Transition:
    def __init__(self, from_state: int, to_state: int, symbol: str):
        self.from_state = from_state
        self.to_state = to_state
        self.symbol = symbol

class AutomataBuilder:
    def __init__(self):
        self.states: Dict[int, State] = {}
        self.transitions: List[Transition] = []
        self.next_state_id = 0
        self.selected_state = None
        self.dragging = False
        self.page = None
        self.canvas = None
        self.status_text = None
        self.input_field = None
        self.result_text = None
        self.symbol_field = None
        self.mode = "DFA"
        self.add_state_mode = False
        self.transition_mode = False
        self.transition_start_state = None
    
    def add_state(self, x: float, y: float) -> int:
        state_id = self.next_state_id
        self.states[state_id] = State(state_id, x, y)
        self.next_state_id += 1
        return state_id
    
    def remove_state(self, state_id: int):
        if state_id in self.states:
            del self.states[state_id]
        self.transitions = [t for t in self.transitions 
                          if t.from_state != state_id and t.to_state != state_id]
    
    def add_transition(self, from_state: int, to_state: int, symbol: str):
        # Remove existing transition between same states with same symbol
        self.transitions = [t for t in self.transitions 
                          if not (t.from_state == from_state and t.to_state == to_state and t.symbol == symbol)]
        
        transition = Transition(from_state, to_state, symbol)
        self.transitions.append(transition)
    
    def set_start_state(self, state_id: int):
        if state_id in self.states:
            # Remove start state from all other states
            for state in self.states.values():
                state.is_start = False
            self.states[state_id].is_start = True
    
    def set_final_state(self, state_id: int):
        if state_id in self.states:
            self.states[state_id].is_final = True
    
    def set_normal_state(self, state_id: int):
        if state_id in self.states:
            self.states[state_id].is_start = False
            self.states[state_id].is_final = False
    
    def build_dfa(self) -> Optional[DFA]:
        """Build a DFA from the current graph"""
        try:
            # Get states
            states = set(str(state_id) for state_id in self.states.keys())
            
            # Get input symbols
            input_symbols = set()
            for transition in self.transitions:
                if transition.symbol and transition.symbol != "ε":
                    input_symbols.add(transition.symbol)
            
            if not input_symbols:
                input_symbols = {'a', 'b'}  # Default symbols
            
            # Get transitions
            transitions = {}
            for transition in self.transitions:
                from_state = str(transition.from_state)
                to_state = str(transition.to_state)
                symbol = transition.symbol
                
                if symbol == "ε":
                    continue  # Skip epsilon transitions for DFA
                
                if from_state not in transitions:
                    transitions[from_state] = {}
                transitions[from_state][symbol] = to_state
            
            # Get initial state
            initial_state = None
            for state_id, state in self.states.items():
                if state.is_start:
                    initial_state = str(state_id)
                    break
            
            if not initial_state:
                return None
            
            # Get final states
            final_states = set()
            for state_id, state in self.states.items():
                if state.is_final:
                    final_states.add(str(state_id))
            
            return DFA(
                states=states,
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states
            )
        except Exception as e:
            print(f"Error building DFA: {e}")
            return None
    
    def build_nfa(self) -> Optional[NFA]:
        """Build an NFA from the current graph"""
        try:
            # Get states
            states = set(str(state_id) for state_id in self.states.keys())
            
            # Get input symbols
            input_symbols = set()
            for transition in self.transitions:
                if transition.symbol:
                    input_symbols.add(transition.symbol)
            
            if not input_symbols:
                input_symbols = {'a', 'b'}  # Default symbols
            
            # Get transitions
            transitions = {}
            for transition in self.transitions:
                from_state = str(transition.from_state)
                to_state = str(transition.to_state)
                symbol = transition.symbol
                
                if from_state not in transitions:
                    transitions[from_state] = {}
                if symbol not in transitions[from_state]:
                    transitions[from_state][symbol] = set()
                transitions[from_state][symbol].add(to_state)
            
            # Get initial state
            initial_state = None
            for state_id, state in self.states.items():
                if state.is_start:
                    initial_state = str(state_id)
                    break
            
            if not initial_state:
                return None
            
            # Get final states
            final_states = set()
            for state_id, state in self.states.items():
                if state.is_final:
                    final_states.add(str(state_id))
            
            return NFA(
                states=states,
                input_symbols=input_symbols,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states
            )
        except Exception as e:
            print(f"Error building NFA: {e}")
            return None
    
    def run_automata(self, input_string: str) -> Tuple[bool, List]:
        """Run the automata on input string"""
        if self.mode == "DFA":
            dfa = self.build_dfa()
            if dfa is None:
                return False, ["Error: Invalid DFA configuration"]
            
            try:
                # Validate input symbols
                for symbol in input_string:
                    if symbol not in dfa.input_symbols:
                        return False, [f"Error: Symbol '{symbol}' not in input symbols {dfa.input_symbols}"]
                
                # Run DFA
                is_accepted = dfa.accepts_input(input_string)
                
                # Get path (simulate step by step)
                path = []
                current_state = dfa.initial_state
                path.append(int(current_state))
                
                for symbol in input_string:
                    if current_state in dfa.transitions and symbol in dfa.transitions[current_state]:
                        current_state = dfa.transitions[current_state][symbol]
                        path.append(int(current_state))
                    else:
                        path.append(-1)  # Invalid state
                        break
                
                return is_accepted, path
                
            except Exception as e:
                return False, [f"Error: {str(e)}"]
        
        else:  # NFA
            nfa = self.build_nfa()
            if nfa is None:
                return False, ["Error: Invalid NFA configuration"]
            
            try:
                # Validate input symbols (skip epsilon)
                for symbol in input_string:
                    if symbol != "ε" and symbol not in nfa.input_symbols:
                        return False, [f"Error: Symbol '{symbol}' not in input symbols {nfa.input_symbols}"]
                
                # Run NFA
                is_accepted = nfa.accepts_input(input_string)
                
                # Get possible states at each step
                state_sets = []
                current_states = {nfa.initial_state}
                state_sets.append(set(int(s) for s in current_states))
                for symbol in input_string:
                    next_states = set()
                    for state in current_states:
                        if state in nfa.transitions and symbol in nfa.transitions[state]:
                            next_states.update(nfa.transitions[state][symbol])
                    # Get epsilon closure
                    if next_states:
                        current_states = next_states
                    else:
                        current_states = set()
                    state_sets.append(set(int(s) for s in current_states))
                
                return is_accepted, state_sets
                
            except Exception as e:
                return False, [f"Error: {str(e)}"]
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "DFA/NFA Builder with automata-lib"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.window.width = 1200
        page.window.height = 800
        
        # Create controls
        self.create_controls()
        
        # Create canvas
        self.canvas = ft.Container(
            content=ft.GestureDetector(
                on_pan_start=self.on_pan_start,
                on_pan_update=self.on_pan_update,
                on_pan_end=self.on_pan_end,
                on_tap=self.on_tap,
            ),
            width=700,
            height=500,
            bgcolor=ft.Colors.GREY_100,
            border=ft.border.all(2, ft.Colors.BLACK),
            border_radius=10,
        )
        
        # Set up keyboard events
        page.on_keyboard_event = self.on_keyboard
        
        # Layout
        controls_row = ft.Row([
            self.mode_dropdown,
            ft.ElevatedButton("Add State", on_click=self.add_state_click),
            ft.ElevatedButton("Clear All", on_click=self.clear_all, bgcolor=ft.Colors.RED_400),
            self.status_text,
        ], alignment=ft.MainAxisAlignment.START)
        
        symbol_row = ft.Row([
            ft.Text("Transition Symbol:", weight=ft.FontWeight.BOLD),
            self.symbol_field,
            ft.Text("(use 'ε' for epsilon)", size=12, color=ft.Colors.GREY),
        ], alignment=ft.MainAxisAlignment.START)
        
        input_row = ft.Row([
            self.input_field,
            ft.ElevatedButton("Run Automata", on_click=self.run_automata_click, bgcolor=ft.Colors.GREEN_400),
        ], alignment=ft.MainAxisAlignment.START)
        
        # Main layout
        page.add(
            controls_row,
            symbol_row,
            ft.Divider(height=20),
            ft.Row([
                ft.Column([
                    ft.Text("Canvas:", weight=ft.FontWeight.BOLD, size=16),
                    self.canvas,
                    ft.Divider(height=10),
                    input_row,
                    self.result_text,
                ], expand=True),
                ft.VerticalDivider(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Instructions:", weight=ft.FontWeight.BOLD, size=16),
                        ft.Text("• Click 'Add State' then click on canvas", size=14),
                        ft.Text("• Drag states to move them", size=14),
                        ft.Text("• Click a state to select it", size=14),
                        ft.Text("• Keyboard Shortcuts:", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("  S - Set as START state", size=12, color=ft.Colors.GREEN),
                        ft.Text("  E - Set as FINAL state", size=12, color=ft.Colors.RED),
                        ft.Text("  N - Set as NORMAL state", size=12, color=ft.Colors.BLUE),
                        ft.Text("  T - Toggle TRANSITION mode", size=12, color=ft.Colors.ORANGE),
                        ft.Text("  Delete - Remove selected state", size=12, color=ft.Colors.RED),
                        ft.Text("State Colors:", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("• START: Green", size=12, color=ft.Colors.GREEN),
                        ft.Text("• FINAL: Red", size=12, color=ft.Colors.RED),
                        ft.Text("• START+FINAL: Purple", size=12, color=ft.Colors.PURPLE),
                        ft.Text("• NORMAL: Blue", size=12, color=ft.Colors.BLUE),
                        ft.Text("• SELECTED: Orange border", size=12, color=ft.Colors.ORANGE),
                        ft.Text("Transition Mode:", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("• Press 'T' to enter transition mode", size=12),
                        ft.Text("• Click source state, then target state", size=12),
                        ft.Text("• Use 'ε' for epsilon transitions (NFA only)", size=12),
                    ], spacing=8),
                    width=300,
                    padding=15,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10,
                )
            ])
        )
        
        self.update_canvas()
    
    def create_controls(self):
        self.mode_dropdown = ft.Dropdown(
            label="Automata Type",
            options=[
                ft.dropdown.Option("DFA"),
                ft.dropdown.Option("NFA"),
            ],
            value="DFA",
            on_change=self.on_mode_change,
            width=150
        )
        
        self.status_text = ft.Text("Ready - Click 'Add State' to begin", size=16, weight=ft.FontWeight.BOLD)
        
        self.symbol_field = ft.TextField(
            label="Transition Symbol",
            value="a",
            width=120
        )
        
        self.input_field = ft.TextField(
            label="Input String to Test",
            hint_text="Enter string like 'aaabbb'",
            width=200,
            expand=True
        )
        
        self.result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    
    def on_keyboard(self, e: ft.KeyboardEvent):
        if e.key == "S" or e.key == "s":
            self.start_state_setter()
        elif e.key == "E" or e.key == "e":
            self.final_state_setter()
        elif e.key == "N" or e.key == "n":
            self.normal_state_setter()
        elif e.key == "T" or e.key == "t":
            self.toggle_transition_mode()
        elif e.key == "Delete":
            self.delete_selected_state()
        
        self.update_canvas()
    
    def start_state_setter(self):
        if self.selected_state is not None:
            self.set_start_state(self.selected_state)
            self.status_text.value = f"State {self.selected_state} set as START"
    
    def final_state_setter(self):
        if self.selected_state is not None:
            self.set_final_state(self.selected_state)
            self.status_text.value = f"State {self.selected_state} set as FINAL"
    
    def normal_state_setter(self):
        if self.selected_state is not None:
            self.set_normal_state(self.selected_state)
            self.status_text.value = f"State {self.selected_state} set as NORMAL"
    
    def toggle_transition_mode(self):
        self.transition_mode = not self.transition_mode
        if self.transition_mode:
            self.status_text.value = "TRANSITION MODE: Click source state"
            self.transition_start_state = None
        else:
            self.status_text.value = "Transition mode exited"
            self.transition_start_state = None
    
    def delete_selected_state(self):
        if self.selected_state is not None:
            state_id = self.selected_state
            self.remove_state(state_id)
            self.selected_state = None
            self.status_text.value = f"Deleted state {state_id}"
    
    def on_mode_change(self, e):
        self.mode = self.mode_dropdown.value
        self.status_text.value = f"Mode: {self.mode} - Click 'Add State' to add states"
        self.page.update()
    
    def add_state_click(self, e):
        self.add_state_mode = True
        self.transition_mode = False
        self.status_text.value = "Click on the canvas to add a state"
        self.page.update()
    
    def clear_all(self, e):
        self.states.clear()
        self.transitions.clear()
        self.next_state_id = 0
        self.selected_state = None
        self.add_state_mode = False
        self.transition_mode = False
        self.transition_start_state = None
        self.update_canvas()
        self.status_text.value = "Cleared all - Click 'Add State' to begin"
        self.result_text.value = ""
        self.page.update()
    
    def on_pan_start(self, e: ft.DragStartEvent):
        if not hasattr(e, 'local_x') or not hasattr(e, 'local_y'):
            return
            
        x, y = e.local_x or 0, e.local_y or 0
        
        # Check if clicking on a state
        for state_id, state in self.states.items():
            if self.distance(x, y, state.x, state.y) <= state.radius:
                self.selected_state = state_id
                self.dragging = True
                
                # Handle transition mode
                if self.transition_mode:
                    if self.transition_start_state is None:
                        # First click - set source state
                        self.transition_start_state = state_id
                        self.status_text.value = f"TRANSITION MODE: Source state {state_id} selected, click target state"
                    else:
                        # Second click - create transition
                        if self.transition_start_state != state_id:
                            symbol = self.symbol_field.value or "a"
                            self.add_transition(self.transition_start_state, state_id, symbol)
                            self.status_text.value = f"Added transition {self.transition_start_state} → {state_id} with '{symbol}'"
                        else:
                            self.status_text.value = "Cannot create transition to same state"
                        
                        # Exit transition mode after creating transition
                        self.transition_mode = False
                        self.transition_start_state = None
                else:
                    self.status_text.value = f"Selected state {state_id} - Drag to move (S:Start, E:Final, N:Normal, T:Transition)"
                
                self.update_canvas()
                return
        
        # If no state clicked and we're in add state mode
        if self.add_state_mode:
            state_id = self.add_state(x, y)
            self.selected_state = state_id
            self.dragging = True
            self.add_state_mode = False
            self.status_text.value = f"Added state {state_id} - Drag to reposition (S:Start, E:Final, N:Normal, T:Transition)"
            self.update_canvas()
    
    def on_pan_update(self, e: ft.DragUpdateEvent):
        if self.dragging and self.selected_state is not None:
            state = self.states[self.selected_state]
            state.x += e.delta_x
            state.y += e.delta_y
            self.update_canvas()
    
    def on_pan_end(self, e: ft.DragEndEvent):
        self.dragging = False
        self.update_canvas()
    
    def on_tap(self, e: ft.TapEvent):
        if not hasattr(e, 'local_x') or not hasattr(e, 'local_y'):
            return
            
        x, y = e.local_x or 0, e.local_y or 0
        
        # Handle transition mode
        if self.transition_mode:
            for state_id, state in self.states.items():
                if self.distance(x, y, state.x, state.y) <= state.radius:
                    if self.transition_start_state is None:
                        # First click - set source state
                        self.transition_start_state = state_id
                        self.selected_state = state_id
                        self.status_text.value = f"TRANSITION MODE: Source state {state_id} selected, click target state"
                    else:
                        # Second click - create transition
                        if self.transition_start_state != state_id:
                            symbol = self.symbol_field.value or "a"
                            self.add_transition(self.transition_start_state, state_id, symbol)
                            self.status_text.value = f"Added transition {self.transition_start_state} → {state_id} with '{symbol}'"
                        else:
                            self.status_text.value = "Cannot create transition to same state"
                        
                        # Exit transition mode after creating transition
                        self.transition_mode = False
                        self.transition_start_state = None
                        self.selected_state = state_id
                    self.update_canvas()
                    return
        
        # Regular click (not in transition mode)
        for state_id, state in self.states.items():
            if self.distance(x, y, state.x, state.y) <= state.radius:
                self.selected_state = state_id
                self.status_text.value = f"Selected state {state_id} (S:Start, E:Final, N:Normal, T:Transition)"
                self.update_canvas()
                return
        
        # Click on empty space - add state if in add mode, otherwise deselect
        if self.add_state_mode:
            state_id = self.add_state(x, y)
            self.selected_state = state_id
            self.add_state_mode = False
            self.status_text.value = f"Added state {state_id} (S:Start, E:Final, N:Normal, T:Transition)"
            self.update_canvas()
        else:
            self.selected_state = None
            self.status_text.value = "Ready - Select a state or click 'Add State'"
            self.update_canvas()
    
    def distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def update_canvas(self):
        canvas_content = []
        
        # Draw transitions
        for transition in self.transitions:
            from_state = self.states[transition.from_state]
            to_state = self.states[transition.to_state]
            
            # Calculate line properties
            dx = to_state.x - from_state.x
            dy = to_state.y - from_state.y
            length = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx);
            
            if length == 0:
                continue
                
            # Normalize
            dx, dy = dx/length, dy/length
            
            # Start and end points (adjusted for state radius)
            start_x = from_state.x + math.cos(angle) * from_state.radius
            start_y = from_state.y + math.sin(angle) * from_state.radius
            end_x = to_state.x - math.cos(angle) * to_state.radius
            end_y = to_state.y - math.sin(angle) * to_state.radius
            
            # Calculate line length and angle
            line_length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            
            # Create line as a rotated container
            line_container = ft.Container(
                width=line_length,
                height=2,
                bgcolor=ft.Colors.BLACK,
                left=start_x,
                top=start_y,
                rotate=ft.Rotate(angle, alignment=ft.alignment.center_left)
            )
            canvas_content.append(line_container)
            
            # Draw arrowhead
            arrow_size = 8

            # Draw arrowhead as two lines
            arrow_line1 = ft.Container(
                width=arrow_size,
                height=2,
                bgcolor=ft.Colors.BLACK,
                left=end_x,
                top=end_y,
                rotate=ft.Rotate(angle - 5 * math.pi / 6, 
                               alignment=ft.alignment.center_left)
            )
            arrow_line2 = ft.Container(
                width=arrow_size,
                height=2,
                bgcolor=ft.Colors.BLACK,
                left=end_x,
                top=end_y,
                rotate=ft.Rotate(angle + 5 * math.pi / 6, 
                               alignment=ft.alignment.center_left)
            )
            
            canvas_content.append(arrow_line1)
            canvas_content.append(arrow_line2)
            
            # Draw transition symbol
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            offset = 15
            symbol_x = mid_x - offset * math.sin(angle)
            symbol_y = mid_y + offset * math.cos(angle)
            
            symbol_text = ft.Text(
                transition.symbol,
                left=symbol_x,
                top=symbol_y,
                color=ft.Colors.BLUE,
                weight=ft.FontWeight.BOLD,
                size=14
            )
            canvas_content.append(symbol_text)
        
        # Draw states
        for state_id, state in self.states.items():
            # Determine state color
            if state.is_start and state.is_final:
                color = ft.Colors.PURPLE
            elif state.is_start:
                color = ft.Colors.GREEN
            elif state.is_final:
                color = ft.Colors.RED
            else:
                color = ft.Colors.BLUE
            
            # State circle
            border_color = ft.Colors.ORANGE if state_id == self.selected_state else ft.Colors.BLACK
            
            circle = ft.Container(
                content=ft.CircleAvatar(
                    radius=state.radius,
                    bgcolor=color,
                ),
                left=state.x - state.radius,
                top=state.y - state.radius,
                border=ft.border.all(3, border_color),
                border_radius=state.radius,
            )
            canvas_content.append(circle)
            
            # State label
            label = ft.Text(
                f"q{state_id}",
                left=state.x - 10,
                top=state.y - 10,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=14
            )
            canvas_content.append(label)
            
            # Start state arrow
            if state.is_start:
                self.draw_start_arrow(canvas_content, state)
        
        # Update the canvas
        self.canvas.content.content = ft.Stack(canvas_content)
        self.page.update()
    
    def draw_start_arrow(self, canvas_content, state: State):
        start_x = state.x - state.radius - 30
        start_y = state.y
        end_x = state.x - state.radius
        end_y = state.y
        
        # Draw line
        line_length = 30
        line = ft.Container(
            width=line_length,
            height=2,
            bgcolor=ft.Colors.BLACK,
            left=start_x,
            top=start_y,
        )
        canvas_content.append(line)
        
        # Draw arrowhead
        arrow_size = 8
        arrow_line1 = ft.Container(
            width=arrow_size,
            height=2,
            bgcolor=ft.Colors.BLACK,
            left=end_x,
            top=end_y,
            rotate=ft.Rotate(-45, alignment=ft.alignment.center_left)
        )
        arrow_line2 = ft.Container(
            width=arrow_size,
            height=2,
            bgcolor=ft.Colors.BLACK,
            left=end_x,
            top=end_y,
            rotate=ft.Rotate(45, alignment=ft.alignment.center_left)
        )
        
        canvas_content.append(arrow_line1)
        canvas_content.append(arrow_line2)
    
    def run_automata_click(self, e):
        input_string = self.input_field.value
        if not input_string:
            self.result_text.value = "Please enter an input string"
            self.result_text.color = ft.Colors.RED
            self.page.update()
            return
        
        if not any(state.is_start for state in self.states.values()):
            self.result_text.value = "No start state defined!"
            self.result_text.color = ft.Colors.RED
            self.page.update()
            return
        
        accepted, result = self.run_automata(input_string)
        
        if accepted:
            self.result_text.value = f"✓ ACCEPTED: '{input_string}'\nResult: {result}"
            self.result_text.color = ft.Colors.GREEN
        else:
            if isinstance(result, list) and result and isinstance(result[0], str) and "Error" in result[0]:
                self.result_text.value = f"✗ ERROR: {result[0]}"
                self.result_text.color = ft.Colors.RED
            else:
                self.result_text.value = f"✗ REJECTED: '{input_string}'\nResult: {result}"
                self.result_text.color = ft.Colors.RED
        
        self.page.update()

def main():
    ft.app(target=AutomataBuilder().main)

if __name__ == "__main__":
    main()
