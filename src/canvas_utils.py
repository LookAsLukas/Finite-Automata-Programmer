import math
from linal import Vector2D, dot_product
from fap import Application
from graph import Node, Transition


def get_clicked_node(x: float, y: float, app: Application) -> Node:
    """Определяет, по какому узлу кликнули."""
    for node in app.graph.nodes:
        if (Vector2D.from_node(node) - Vector2D(x, y)).length() <= app.config.node_radius:
            return node
    return None


def check_self_transition(click: Vector2D, transition: Transition, app: Application) -> bool:
    state_p = Vector2D.from_node(transition.start)
    out_phis = {
        Vector2D.from_transition(transition_).phi()
        for transition_ in app.graph.transitions
        if transition_.start == transition.start and
        transition_.end != transition.end
    }
    in_phis = {
        (-Vector2D.from_transition(transition_)).phi()
        for transition_ in app.graph.transitions
        if transition_.end == transition.end and
        transition_.start != transition.start
    }
    taken = sorted(out_phis | in_phis)

    arc_radius = 5/6 * app.config.node_radius

    if taken == []:
        taken = [math.pi / 4]
    taken.append(taken[0] + 2 * math.pi)

    diffs = [phi2 - phi1 for phi1, phi2 in zip(taken, taken[1:])]
    max_diff = max(diffs)

    arc_center_dir = Vector2D.from_phi_r(taken[diffs.index(max_diff)] + max_diff / 2, 1)
    contact_offset_phi = min(math.pi / 4, max_diff / 2)
    contact1 = state_p + arc_center_dir.turned(contact_offset_phi) * app.config.node_radius
    contact2 = state_p + arc_center_dir.turned(-contact_offset_phi) * app.config.node_radius

    # arc_radius^2 = (d + (1 - cos(contact_offset_phi)) * node_radius)^2 + (sin(contact_offset_phi) * node_radius)^2
    # d = node_radius * (cos(contact_offset_phi) - 1) + sqrt(arc_radius^2 - (node_radius * sin(contact_offset_phi))^2)
    center_distance = app.config.node_radius * math.cos(contact_offset_phi) + math.sqrt(arc_radius ** 2 - (app.config.node_radius * math.sin(contact_offset_phi)) ** 2)
    arc_center = state_p + arc_center_dir * center_distance

    start_angle = ((contact2 - arc_center).phi() + 2 * math.pi) % (2 * math.pi)
    end_angle = ((contact1 - arc_center).phi() + 2 * math.pi) % (2 * math.pi)

    threshold = 5
    click_angle = ((click - arc_center).phi() + 2 * math.pi) % (2 * math.pi)
    click_d = (click - arc_center).length()
    if end_angle < start_angle:
        return ((0 <= click_angle <= end_angle) or (start_angle <= click_angle <= 2 * math.pi)) and \
               abs(click_d - arc_radius) <= threshold
    return start_angle <= click_angle <= end_angle and \
           abs(click_d - arc_radius) <= threshold


def get_clicked_transition(x: float, y: float, app: Application) -> Transition:
    """Определяет, по какому переходу кликнули."""
    threshold = 5
    click = Vector2D(x, y)
    for transition in app.graph.transitions:
        if transition.start == transition.end:
            if check_self_transition(click, transition, app):
                return transition
            continue

        start_p = Vector2D.from_node(transition.start)
        end_p = Vector2D.from_node(transition.end)

        double = False
        for transition_ in app.graph.transitions:
            if transition_.end == transition.start and \
               transition_.start == transition.end:
                double = True
                break

        dir = (end_p - start_p).normalized()
        if double:
            line_gap = 10
            start_p += dir.turned(-math.asin(line_gap / 2 / app.config.node_radius)) * app.config.node_radius
            end_p -= dir.turned(math.asin(line_gap / 2 / app.config.node_radius)) * app.config.node_radius
        else:
            start_p += dir * app.config.node_radius
            end_p -= dir * app.config.node_radius

        # Let's call start point A, click point B,
        # End point C and distance point D
        ab = click - start_p
        ac = end_p - start_p
        ad_len = dot_product(ab, ac) / ac.length()
        bd_len = math.sqrt(ab.length() ** 2 - ad_len ** 2)
        if bd_len <= threshold and 0 <= ad_len <= ac.length():
            return transition

    return None
