import pytest
import sys
import os
from automata_io import save_automaton_to_json, load_automaton_from_json
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from json import load
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


temp_file = "tests/tmp/tmp.fa"


def cmp_fa_files(path1, path2):
    with open(path1, 'r') as expected, \
         open(path2, 'r') as generated:
        expected = load(expected)
        generated = load(generated)
        expected["states"] = set(expected["states"])
        generated["states"] = set(generated["states"])
        expected["final_states"] = set(expected["final_states"])
        generated["final_states"] = set(generated["final_states"])
        expected["input_symbols"] = set(expected["input_symbols"])
        generated["input_symbols"] = set(generated["input_symbols"])
        expected["transitions"] = {
            k1: {k2: set(v2) for k2, v2 in v1.items()}
            for k1, v1 in expected["transitions"].items()
        }
        generated["transitions"] = {
            k1: {k2: set(v2) for k2, v2 in v1.items()}
            for k1, v1 in generated["transitions"].items()
        }
        return expected == generated


def test_save_dfa():
    fa = DFA(
        states={'a', 'b', 'c'},
        input_symbols={'0', '1'},
        transitions={
            'a': {
                '0': 'b',
                '1': 'c',
            },
            'b': {
                '0': 'b',
                '1': 'b',
            },
            'c': {
                '0': 'b',
                '1': 'a',
            }
        },
        initial_state='a',
        final_states={'a'}
    )
    save_automaton_to_json(fa, temp_file)
    assert os.path.exists(temp_file)
    assert cmp_fa_files("tests/misc/test_dfa.fa", temp_file)


def test_save_nfa():
    fa = NFA(
        states={'a', 'b', 'c'},
        input_symbols={'0', '1'},
        transitions={
            'a': {
                '1': {'b'},
            },
            'b': {
                '1': {'a'},
            },
        },
        initial_state='a',
        final_states={'a'}
    )
    save_automaton_to_json(fa, temp_file)
    assert os.path.exists(temp_file)
    assert cmp_fa_files("tests/misc/test_nfa.fa", temp_file)


def test_save_crash():
    with pytest.raises(TypeError):
        save_automaton_to_json(0, "lol/lol/lol")


def test_load_dfa():
    fa = DFA(
        states={'a', 'b', 'c'},
        input_symbols={'0', '1'},
        transitions={
            'a': {
                '0': 'b',
                '1': 'c',
            },
            'b': {
                '0': 'b',
                '1': 'b',
            },
            'c': {
                '0': 'b',
                '1': 'a',
            }
        },
        initial_state='a',
        final_states={'a'}
    )
    got = load_automaton_from_json("tests/misc/test_dfa.fa")
    assert fa == got


def test_load_nfa():
    fa = NFA(
        states={'a', 'b', 'c'},
        input_symbols={'0', '1'},
        transitions={
            'a': {
                '1': {'b'},
            },
            'b': {
                '1': {'a'},
            },
        },
        initial_state='a',
        final_states={'a'}
    )
    got = load_automaton_from_json("tests/misc/test_nfa.fa")
    assert fa == got
