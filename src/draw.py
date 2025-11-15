import math
import flet
from flet import TextStyle, canvas, Colors, FontWeight


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
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx ** 2 + dy ** 2)
            if length == 0:
                continue
            ux, uy = dx / length, dy / length
            start_x, start_y = x1 + ux * 30, y1 + uy * 30
            end_x, end_y = x2 - ux * 30, y2 - uy * 30

            elements.append(canvas.Line(
                x1=start_x, y1=start_y, x2=end_x, y2=end_y,
                paint=flet.Paint(Colors.BLACK, stroke_width=2)
            ))

            arrow_size = 10
            perp_x, perp_y = -uy, ux
            elements.append(canvas.Line(
                x1=end_x, y1=end_y,
                x2=end_x - ux * arrow_size + perp_x * arrow_size,
                y2=end_y - uy * arrow_size + perp_y * arrow_size,
                paint=flet.Paint(Colors.BLACK, stroke_width=2)
            ))
            elements.append(canvas.Line(
                x1=end_x, y1=end_y,
                x2=end_x - ux * arrow_size - perp_x * arrow_size,
                y2=end_y - uy * arrow_size - perp_y * arrow_size,
                paint=flet.Paint(Colors.BLACK, stroke_width=2)
            ))

            label = canvas.Text(
                x=(x1 + x2) / 2 + 10,
                y=(y1 + y2) / 2 - 10,
                text=symbol,
                style=TextStyle(size=18, weight=FontWeight.BOLD)
            )
            elements.append(label)

    return elements
