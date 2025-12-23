import math
import flet
from flet import TextStyle, canvas, Colors, FontWeight
from linal import Vector2D, dot_product


def draw_nodes(attr, ui):
    elements = []
    for name, (x, y) in attr.nodes.items():
        is_start = name == attr.start_state
        is_final = name in attr.final_states
        
        if is_start and is_final:
            color = Colors.YELLOW  
        elif is_start:
            color = Colors.LIGHT_GREEN_300
        elif is_final:
            color = Colors.PINK_200
        else:
            color = Colors.AMBER_100

        circle = canvas.Circle(x=x, y=y, radius=30, paint=flet.Paint(color))
        elements.append(circle)

        if attr.selected_node == name:
            outline = canvas.Circle(
                x=x, y=y, radius=30,
                paint=flet.Paint(Colors.BLUE_800, style="stroke", stroke_width=3)
            )
            elements.append(outline)

        text = canvas.Text(
            x=x - 12, y=y - 10,
            text=name,
            style=TextStyle(weight=FontWeight.BOLD)
        )
        elements.append(text)

    transition_elements = draw_transitions(attr, ui)
    ui.drawing_area.shapes = elements + transition_elements
    ui.drawing_area.update()


def calc_self_line(symbols, paint, point: Vector2D, taken):
    arc_radius = 25

    taken = sorted(taken)
    if taken == []:
        taken = [math.pi / 4]
    taken.append(taken[0] + 2 * math.pi)

    diffs = [phi2 - phi1 for phi1, phi2 in zip(taken, taken[1:])]
    max_diff = max(diffs)

    arc_center_dir = Vector2D.from_phi_r(taken[diffs.index(max_diff)] + max_diff / 2, 1)
    contact_offset_phi = min(math.pi / 4, max_diff / 2)
    contact1 = point + arc_center_dir.turned(contact_offset_phi) * 30
    contact2 = point + arc_center_dir.turned(-contact_offset_phi) * 30

    # arc_radius^2 = (d + (1 - cos(contact_offset_phi)) * 30)^2 + (sin(contact_offset_phi) * 30)^2
    # d = 30 * (cos(contact_offset_phi) - 1) + sqrt(arc_radius^2 - (30 * sin(contact_offset_phi))^2)
    center_distance = 30 * math.cos(contact_offset_phi) + math.sqrt(arc_radius ** 2 - (30 * math.sin(contact_offset_phi)) ** 2)
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
            paint=flet.Paint(
                paint.color,
                stroke_width=paint.stroke_width,
                style=flet.PaintingStyle.STROKE
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
            alignment=flet.alignment.center,
            rotate=text_rotation
        )
    ]


def calc_line(symbols, paint, start: Vector2D, end: Vector2D, double):
    dir = (end - start).normalized()
    line_start = start
    line_end = end
    if double:
        line_gap = 10
        line_start += dir.turned(-math.asin(line_gap / 2 / 30)) * 30
        line_end -= dir.turned(math.asin(line_gap / 2 / 30)) * 30
    else:
        line_start += dir * 30
        line_end -= dir * 30

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
            alignment=flet.alignment.center,
            rotate=text_rotation
        )
    ]


def draw_transitions(attr, ui):
    elements = []
    for start, trans_list in attr.transitions.items():
        if start not in attr.nodes:
            continue
        (x1, y1) = attr.nodes[start]

        unique_trans_list = {
            t["end"]: t
            for t in trans_list
        }.values()
        for t in unique_trans_list:
            symbols = ', '.join({
                tt["symbol"]
                for tt in trans_list
                if tt["end"] == t["end"]
            })
            end = t["end"]
            if end not in attr.nodes:
                continue

            (x2, y2) = attr.nodes[end]
            start_p = Vector2D(x1, y1)
            end_p = Vector2D(x2, y2)

            is_selected = attr.selected_transition == (start, end)

            line_color = Colors.BLUE_800 if is_selected else Colors.BLACK
            line_width = 3 if is_selected else 2
            if start == end:
                taken_out = {
                    (Vector2D.from_tuple(attr.nodes[tt["end"]]) - start_p).phi()
                    for tt in trans_list
                    if start != tt["end"]
                }
                taken_in = {
                    (Vector2D.from_tuple(attr.nodes[_start]) - start_p).phi()
                    for _start, _trans_list in attr.transitions.items()
                    if start in map(lambda x: x["end"], _trans_list) and start != _start
                }
                elements += calc_self_line(
                    symbols,
                    flet.Paint(line_color, stroke_width=line_width),
                    start_p,
                    taken_out | taken_in
                )
                continue

            double = False
            for tt in attr.transitions.get(end, []):
                if tt["end"] == start:
                    double = True
                    break

            elements += calc_line(
                symbols,
                flet.Paint(line_color, stroke_width=line_width),
                start_p, end_p,
                double
            )

    return elements
