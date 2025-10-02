from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from typing import Dict, List, Optional
from graph import State, Transition


class AutomataBuilder:
    def __init__(self):
        self.states: Dict[int, State] = {}
        self.transitions: List[Transition] = []
        self.next_state_id = 0
    
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
