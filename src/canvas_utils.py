import math
from typing import Tuple, Optional, Dict, List, Any


def get_clicked_node(x: float, y: float, nodes: Dict[str, Tuple[float, float]]) -> Optional[str]:
    """Определяет, по какому узлу кликнули."""
    for name, (nx, ny) in nodes.items():
        if (x - nx) ** 2 + (y - ny) ** 2 <= 30 ** 2:
            return name
    return None


def get_clicked_transition(x: float, y: float, nodes: Dict[str, Tuple[float, float]], 
                          transitions: Dict[str, List[Dict[str, Any]]]) -> Tuple[Optional[str], Optional[Dict]]:
    """Определяет, по какому переходу кликнули."""
    threshold = 10  
    for start, trans_list in transitions.items():
        if start not in nodes:
            continue
        (x1, y1) = nodes[start]
        for t in trans_list:
            end = t["end"]
            if end not in nodes:
                continue
            (x2, y2) = nodes[end]

            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx ** 2 + dy ** 2)
            if length == 0:
                continue

            ux, uy = dx / length, dy / length
            start_x, start_y = x1 + ux * 30, y1 + uy * 30
            end_x, end_y = x2 - ux * 30, y2 - uy * 30

            px, py = x, y
            line_dist = abs((end_y - start_y) * px - (end_x - start_x) * py + end_x * start_y - end_y * start_x) / length
            if line_dist <= threshold:
                dot = ((px - start_x) * (end_x - start_x) + (py - start_y) * (end_y - start_y)) / (length ** 2)
                if 0 <= dot <= 1:
                    return start, t
    return None, None