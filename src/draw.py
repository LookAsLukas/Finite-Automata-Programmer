import math
import flet as ft
from flet import TextStyle, canvas, Colors, FontWeight
from linal import Vector2D, dot_product
from fap import Application
from graph import NodeType
from typing import Set, List


def draw_nodes(app: Application) -> None:
    elements = []
    for node in app.graph.nodes:
        match node.type:
            case NodeType.START_FINAL:
                color = app.config.start_final_node_color
            case NodeType.START:
                color = app.config.start_node_color
            case NodeType.FINAL:
                color = app.config.final_node_color
            case _:
                color = app.config.node_color

        circle = canvas.Circle(
            x=node.x, y=node.y,
            radius=app.config.node_radius,
            paint=ft.Paint(color)
        )
        elements.append(circle)

        if app.attr.debug_mode and node.name in app.attr.current_states:
            glow = canvas.Circle(
                x=node.x, y=node.y,
                radius=app.config.node_radius + 5,
                paint=ft.Paint("#ffff00", style="stroke", stroke_width=4)
            )
            elements.append(glow)

        if app.graph.selected_node == node:
            outline = canvas.Circle(
                x=node.x, y=node.y,
                radius=app.config.node_radius,
                paint=ft.Paint(app.config.selection_color, style="stroke", stroke_width=3)
            )
            elements.append(outline)

        text = canvas.Text(
            x=node.x, y=node.y,
            text=node.name,
            style=TextStyle(weight=FontWeight.BOLD),
            alignment=ft.alignment.center
        )
        elements.append(text)

    transition_elements = calc_transitions(app)
    app.ui.drawing_area.shapes = elements + transition_elements
    app.ui.drawing_area.update()


def calc_self_line(symbols: str, paint: ft.Paint, point: Vector2D, node_radius: float, taken: Set[float]) -> List:
    arc_radius = 5/6 * node_radius

    taken = sorted(taken)
    if taken == []:
        taken = [math.pi / 4]
    taken.append(taken[0] + 2 * math.pi)

    diffs = [phi2 - phi1 for phi1, phi2 in zip(taken, taken[1:])]
    max_diff = max(diffs)

    arc_center_dir = Vector2D.from_phi_r(taken[diffs.index(max_diff)] + max_diff / 2, 1)
    contact_offset_phi = min(math.pi / 4, max_diff / 2)
    contact1 = point + arc_center_dir.turned(contact_offset_phi) * node_radius
    contact2 = point + arc_center_dir.turned(-contact_offset_phi) * node_radius

    # arc_radius^2 = (d + (1 - cos(contact_offset_phi)) * node_radius)^2 + (sin(contact_offset_phi) * node_radius)^2
    # d = node_radius * (cos(contact_offset_phi) - 1) + sqrt(arc_radius^2 - (node_radius * sin(contact_offset_phi))^2)
    center_distance = node_radius * math.cos(contact_offset_phi) + math.sqrt(arc_radius ** 2 - (node_radius * math.sin(contact_offset_phi)) ** 2)
    arc_center = point + arc_center_dir * center_distance

    start_angle = (contact2 - arc_center).phi()
    contact1_dir = (contact1 - arc_center).normalized()
    contact2_dir = (contact2 - arc_center).normalized()
    sweep_angle = 2 * math.pi - math.acos(dot_product(contact1_dir, contact2_dir))

    arrow_size = 15
    # A bunch of arbitrary shit just to make it look somewhat pretty
    arrow_height = arrow_size * math.cos(25 * math.pi / 180)
    # This is orthocenter btw
    adjustment_chord = 2 * arrow_height - arrow_size ** 2 / arrow_height
    adjutment_angle = math.pi / 2 - math.acos(adjustment_chord / 2 / arc_radius)
    arrow_dir = contact1_dir.perpendicular().turned(-adjutment_angle)
    arrow1 = contact1 + arrow_dir.turned(205 * math.pi / 180) * arrow_size
    arrow2 = contact1 + arrow_dir.turned(155 * math.pi / 180) * arrow_size

    text_distance = 10 + arc_radius
    text_position = arc_center + arc_center_dir * text_distance
    text_rotation = arc_center_dir.perpendicular().phi() + (arc_center_dir.y > 0) * math.pi

    return [
        canvas.Arc(
            x=arc_center.x - arc_radius, y=arc_center.y - arc_radius,
            height=arc_radius * 2, width=arc_radius * 2,
            paint=ft.Paint(
                paint.color,
                stroke_width=paint.stroke_width,
                style=ft.PaintingStyle.STROKE
            ),
            start_angle=start_angle,
            sweep_angle=sweep_angle,
            use_center=False
        ),
        canvas.Line(
            x1=arrow1.x, y1=arrow1.y,
            x2=contact1.x, y2=contact1.y,
            paint=paint
        ),
        canvas.Line(
            x1=arrow2.x, y1=arrow2.y,
            x2=contact1.x, y2=contact1.y,
            paint=paint
        ),
        canvas.Text(
            x=text_position.x, y=text_position.y,
            text=symbols,
            style=TextStyle(size=18, weight=FontWeight.BOLD, color=paint.color),
            alignment=ft.alignment.center,
            rotate=text_rotation
        )
    ]


def calc_line(symbols: str, paint: ft.Paint, start: Vector2D, end: Vector2D, double: bool, node_radius: float) -> List:
    dir = (end - start).normalized()
    line_start = start
    line_end = end
    if double:
        line_gap = 10
        line_start += dir.turned(-math.asin(line_gap / 2 / node_radius)) * node_radius
        line_end -= dir.turned(math.asin(line_gap / 2 / node_radius)) * node_radius
    else:
        line_start += dir * node_radius
        line_end -= dir * node_radius

    arrow_size = 15
    arrow_left = line_end + (dir * arrow_size).turned(205 * math.pi / 180)
    arrow_right = line_end + (dir * arrow_size).turned(155 * math.pi / 180)

    text_position = (line_start + line_end) / 2
    text_distance = 10
    text_rotation = dir.phi() + (start.x > end.x) * math.pi
    if double or start.x < end.x:
        text_position -= dir.perpendicular() * text_distance
    else:
        text_position += dir.perpendicular() * text_distance

    return [
        canvas.Line(
            x1=line_start.x, y1=line_start.y,
            x2=line_end.x, y2=line_end.y,
            paint=paint
        ),
        canvas.Line(
            x1=arrow_left.x, y1=arrow_left.y,
            x2=line_end.x, y2=line_end.y,
            paint=paint
        ),
        canvas.Line(
            x1=arrow_right.x, y1=arrow_right.y,
            x2=line_end.x, y2=line_end.y,
            paint=paint
        ),
        canvas.Text(
            x=text_position.x, y=text_position.y,
            text=symbols,
            style=TextStyle(size=18, weight=FontWeight.BOLD, color=paint.color),
            alignment=ft.alignment.center,
            rotate=text_rotation
        )
    ]


def calc_transitions(app: Application) -> List:
    elements = []
    for transition in app.graph.transitions:
        start_p = Vector2D.from_node(transition.start)
        end_p = Vector2D.from_node(transition.end)

        is_selected = app.graph.selected_transition == transition
        line_color = app.config.selection_color if is_selected else Colors.BLACK
        line_width = 3 if is_selected else 2

        if transition.start == transition.end:
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
            elements += calc_self_line(
                transition.symbols,
                ft.Paint(line_color, stroke_width=line_width),
                start_p,
                app.config.node_radius,
                out_phis | in_phis
            )
            continue

        double = False
        for transition_ in app.graph.transitions:
            if transition_.end == transition.start and transition_.start == transition.end:
                double = True
                break

        elements += calc_line(
            transition.symbols,
            ft.Paint(line_color, stroke_width=line_width),
            start_p, end_p,
            double,
            app.config.node_radius
        )

    return elements
