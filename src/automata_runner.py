from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from typing import List, Tuple


class AutomataRunner:
    def run_dfa(dfa: DFA, input_string: str) -> Tuple[bool, List]:
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

    def run_nfa(nfa: NFA, input_string: str) -> Tuple[bool, List]:
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
