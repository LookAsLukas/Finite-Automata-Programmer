import math
import flet
from flet import TextStyle, canvas, Colors, FontWeight
from linal import Vector2D


def draw_nodes(attr, ui):
    elements = []
    for name, (x, y) in attr.nodes.items():
        if name == attr.start_state:
            color = Colors.LIGHT_GREEN_300
        elif name in attr.final_states:
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


def calc_lines(symbols, paint, start: Vector2D, end: Vector2D, double):
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

        for t in trans_list:
            symbol = t["symbol"]
            end = t["end"]
            if end not in attr.nodes:
                continue

            (x2, y2) = attr.nodes[end]
            start_p = Vector2D(x1, y1)
            end_p = Vector2D(x2, y2)
            if (end_p - start_p).length() == 0:
                continue

            is_selected = attr.selected_transition and \
                          attr.selected_transition[0] == start and \
                          attr.selected_transition[1] == t

            line_color = Colors.BLUE_800 if is_selected else Colors.BLACK
            line_width = 3 if is_selected else 2

            double = False
            for tt in attr.transitions.get(end, []):
                if tt["end"] == start:
                    double = True
                    break

            elements += calc_lines(
                symbol,
                flet.Paint(line_color, stroke_width=line_width),
                start_p, end_p,
                double
            )

    return elements
