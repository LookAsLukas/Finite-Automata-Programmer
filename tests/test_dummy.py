import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from lol1 import *

def test_1():
    assert important(2) == 4


def test_2():
    assert very_important(3, 4) == 0

def test_3():
    assert not_important(69) == 0
