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

            # Let's call start point A, click point B,
            # End point C and distance point D
            ab = (x - start_x, y - start_y)
            ac = (end_x - start_x, end_y - start_y)
            ac_len = math.sqrt(ac[0] ** 2 + ac[1] ** 2)
            ad_len = (ab[0] * ac[0] + ab[1] * ac[1]) / ac_len
            bd_len = math.sqrt((ab[0] ** 2 + ab[1] ** 2) - ad_len ** 2)
            if bd_len <= threshold and 0 <= ad_len <= ac_len:
                return start, t

    return None, None
