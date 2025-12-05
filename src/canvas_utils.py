import math
from typing import Tuple, Optional, Dict, List, Any
from linal import Vector2D, dot_product


def get_clicked_node(x: float, y: float, nodes: Dict[str, Tuple[float, float]]) -> Optional[str]:
    """Определяет, по какому узлу кликнули."""
    for name, (nx, ny) in nodes.items():
        if (x - nx) ** 2 + (y - ny) ** 2 <= 30 ** 2:
            return name
    return None


def get_clicked_transition(x: float, y: float, nodes: Dict[str, Tuple[float, float]], 
                          transitions: Dict[str, List[Dict[str, Any]]]) -> Tuple[Optional[str], Optional[Dict]]:
    """Определяет, по какому переходу кликнули."""
    threshold = 5
    click = Vector2D(x, y)
    for start, trans_list in transitions.items():
        if start not in nodes:
            continue
        (x1, y1) = nodes[start]
        for t in trans_list:
            end = t["end"]
            if end not in nodes:
                continue
            (x2, y2) = nodes[end]

            start_p = Vector2D(x1, y1)
            end_p = Vector2D(x2, y2)
            if (end_p - start_p).length() == 0:
                continue

            double = False
            for tt in transitions.get(end, []):
                if tt["end"] == start:
                    double = True
                    break
            dir = (end_p - start_p).normalized()
            if double:
                line_gap = 10
                start_p += dir.turned(-math.asin(line_gap / 2 / 30)) * 30
                end_p -= dir.turned(math.asin(line_gap / 2 / 30)) * 30
            else:
                start_p += dir * 30
                end_p -= dir * 30

            # Let's call start point A, click point B,
            # End point C and distance point D
            ab = click - start_p
            ac = end_p - start_p
            ad_len = dot_product(ab, ac) / ac.length()
            bd_len = math.sqrt(ab.length() ** 2 - ad_len ** 2)
            if bd_len <= threshold and 0 <= ad_len <= ac.length():
                return start, t

    return None, None
