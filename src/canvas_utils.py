import math
from typing import Tuple, Optional, Dict, List, Any
from linal import Vector2D, dot_product


def get_clicked_node(x: float, y: float, nodes: Dict[str, Tuple[float, float]]) -> Optional[str]:
    """Определяет, по какому узлу кликнули."""
    for name, (nx, ny) in nodes.items():
        if (x - nx) ** 2 + (y - ny) ** 2 <= 30 ** 2:
            return name
    return None


def check_self_transition(click: Vector2D, transitions, nodes, state):
    state_p = Vector2D.from_tuple(nodes[state])
    taken_out = {
        (Vector2D.from_tuple(nodes[tt["end"]]) - state_p).phi()
        for tt in transitions[state]
        if state != tt["end"]
    }
    taken_in = {
        (Vector2D.from_tuple(nodes[_start]) - state_p).phi()
        for _start, _trans_list in transitions.items()
        if state in map(lambda x: x["end"], _trans_list) and state != _start
    }
    taken = sorted(taken_in | taken_out)

    arc_radius = 25

    if taken == []:
        taken = [math.pi / 4]
    taken.append(taken[0] + 2 * math.pi)

    diffs = [phi2 - phi1 for phi1, phi2 in zip(taken, taken[1:])]
    max_diff = max(diffs)

    arc_center_dir = Vector2D.from_phi_r(taken[diffs.index(max_diff)] + max_diff / 2, 1)
    contact_offset_phi = min(math.pi / 4, max_diff / 2)
    contact1 = state_p + arc_center_dir.turned(contact_offset_phi) * 30
    contact2 = state_p + arc_center_dir.turned(-contact_offset_phi) * 30

    # arc_radius^2 = (d + (1 - cos(contact_offset_phi)) * 30)^2 + (sin(contact_offset_phi) * 30)^2
    # d = 30 * (cos(contact_offset_phi) - 1) + sqrt(arc_radius^2 - (30 * sin(contact_offset_phi))^2)
    center_distance = 30 * math.cos(contact_offset_phi) + math.sqrt(arc_radius ** 2 - (30 * math.sin(contact_offset_phi)) ** 2)
    arc_center = state_p + arc_center_dir * center_distance

    start_angle = ((contact2 - arc_center).phi() + 2 * math.pi) % (2 * math.pi)
    end_angle = ((contact1 - arc_center).phi() + 2 * math.pi) % (2 * math.pi)

    threshold = 5
    click_angle = ((click - arc_center).phi() + 2 * math.pi) % (2 * math.pi)
    click_d = (click - arc_center).length()
    if end_angle < start_angle:
        return ((0 <= click_angle <= end_angle) or (start_angle <= click_angle <= 2 * math.pi))\
               and abs(click_d - arc_radius) <= threshold
    return start_angle <= click_angle <= end_angle\
           and abs(click_d - arc_radius) <= threshold


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
            if start == end:
                if check_self_transition(click, transitions, nodes, start):
                    return start, end
                continue
            (x2, y2) = nodes[end]

            start_p = Vector2D(x1, y1)
            end_p = Vector2D(x2, y2)

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
                return start, end

    return None, None
