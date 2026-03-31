import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from debug import get_epsilon_closure

class MockNFA:
    def __init__(self, transitions):
        self.transitions = transitions



def test_no_epsilon_transitions():
    """Тест: Нет эпсилон-переходов. Замыкание должно вернуть только само состояние."""
    nfa = MockNFA({
        "q0": {"a": ["q1"], "b": ["q2"]}
    })
    result = get_epsilon_closure(nfa, {"q0"})
    assert result == {"q0"}

def test_single_epsilon_empty_string():
    """Тест: Один переход по пустой строке ('')."""
    nfa = MockNFA({
        "q0": {"": ["q1"], "a": ["q2"]},
        "q1": {}
    })
    result = get_epsilon_closure(nfa, {"q0"})
    assert result == {"q0", "q1"}

def test_single_epsilon_char():
    """Тест: Один переход по символу 'ε'."""
    nfa = MockNFA({
        "q0": {"ε": ["q1"]},
        "q1": {}
    })
    result = get_epsilon_closure(nfa, {"q0"})
    assert result == {"q0", "q1"}

def test_epsilon_chain():
    """Тест: Цепочка переходов (q0 -> q1 -> q2)."""
    nfa = MockNFA({
        "q0": {"": ["q1"]},
        "q1": {"": ["q2"]},
        "q2": {}
    })
    result = get_epsilon_closure(nfa, {"q0"})
    assert result == {"q0", "q1", "q2"}

def test_epsilon_cycle():
    """Тест: Цикл (q0 -> q1 -> q0). Проверяем, что функция не уйдет в бесконечный цикл."""
    nfa = MockNFA({
        "q0": {"": ["q1"]},
        "q1": {"": ["q0", "q2"]},
        "q2": {}
    })
    result = get_epsilon_closure(nfa, {"q0"})
    assert result == {"q0", "q1", "q2"}

def test_multiple_start_states():
    """Тест: Поиск замыкания сразу для нескольких стартовых состояний."""
    nfa = MockNFA({
        "q0": {"": ["q1"]},
        "q1": {},
        "q2": {"": ["q3"]},
        "q3": {}
    })
    # Передаем сет из двух состояний: {"q0", "q2"}
    result = get_epsilon_closure(nfa, {"q0", "q2"})
    assert result == {"q0", "q1", "q2", "q3"}

def test_missing_state_in_transitions():
    """Тест: Защита от ошибки KeyError, если состояния нет в словаре переходов."""
    nfa = MockNFA({
        "q0": {"": ["q1"]}
        # q1 отсутствует в словаре transitions
    })
    result = get_epsilon_closure(nfa, {"q0"})
    assert result == {"q0", "q1"}