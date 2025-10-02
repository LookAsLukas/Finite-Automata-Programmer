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

