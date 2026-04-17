from __future__ import annotations

import math
import flet as ft
from flet import TextStyle, canvas, Colors, FontWeight
from linal import Vector2D, dot_product
from graph import NodeType, Graph, Node, Transition
from typing import Set, List
from copy import deepcopy


class Draw:
    def __init__(self, app):
        self.app = app
        self.shapes = {}

    def update_node(self, node: Node):
        related_transitons = [
            transition
            for transition in self.shapes
            if isinstance(transition, Transition) and
            (transition.start == node or transition.end == node)]
        for transition in related_transitons:
            self.update_transition(transition)

        if node not in self.app.graph.nodes:
            for shape in self.shapes.pop(node, []):
                self.app.ui.drawing_area.shapes.remove(shape)
            self.app.ui.drawing_area.update()
            return

        if node not in self.shapes:
            self.shapes[node] = self.render_node(node)
            self.app.ui.drawing_area.shapes.extend(self.shapes[node])
            self.app.ui.drawing_area.update()
            return

        new_shapes = self.render_node(node)
        if len(new_shapes) != len(self.shapes[node]):
            for shape in self.shapes.pop(node, []):
                self.app.ui.drawing_area.shapes.remove(shape)
            self.shapes[node] = self.render_node(node)
            self.app.ui.drawing_area.shapes.extend(self.shapes[node])
            self.app.ui.drawing_area.update()
            return

        for i in range(len(new_shapes)):
            if type(new_shapes[i]) is canvas.Circle:
                self.shapes[node][i].x = new_shapes[i].x
                self.shapes[node][i].y = new_shapes[i].y
                self.shapes[node][i].radius = new_shapes[i].radius
                self.shapes[node][i].paint = new_shapes[i].paint
            elif type(new_shapes[i]) is canvas.Text:
                self.shapes[node][i].x = new_shapes[i].x
                self.shapes[node][i].y = new_shapes[i].y
                self.shapes[node][i].text = new_shapes[i].text
                self.shapes[node][i].style = new_shapes[i].style
                self.shapes[node][i].alignment = new_shapes[i].alignment

            self.shapes[node][i].update()

    def update_transition(self, transition: Transition):
        if transition not in self.app.graph.transitions:
            for shape in self.shapes.pop(transition, []):
                self.app.ui.drawing_area.shapes.remove(shape)
            self.app.ui.drawing_area.update()
            return

        if transition not in self.shapes:
            self.shapes[transition] = self.render_transition(transition)
            self.app.ui.drawing_area.shapes.extend(self.shapes[transition])
            self.app.ui.drawing_area.update()
            return

        new_shapes = self.render_transition(transition)
        if type(new_shapes[0]) is not type(self.shapes[transition][0]):
            for shape in self.shapes.pop(transition, []):
                self.app.ui.drawing_area.shapes.remove(shape)
            self.app.ui.drawing_area.update()
            self.shapes[transition] = self.render_transition(transition)
            self.app.ui.drawing_area.shapes.extend(self.shapes[transition])
            self.app.ui.drawing_area.update()
            return

        for i in range(len(new_shapes)):
            if type(new_shapes[i]) is canvas.Line:
                self.shapes[transition][i].x1 = new_shapes[i].x1
                self.shapes[transition][i].y1 = new_shapes[i].y1
                self.shapes[transition][i].x2 = new_shapes[i].x2
                self.shapes[transition][i].y2 = new_shapes[i].y2
                self.shapes[transition][i].paint = new_shapes[i].paint
            elif type(new_shapes[i]) is canvas.Text:
                self.shapes[transition][i].x = new_shapes[i].x
                self.shapes[transition][i].y = new_shapes[i].y
                self.shapes[transition][i].text = new_shapes[i].text
                self.shapes[transition][i].style = new_shapes[i].style
                self.shapes[transition][i].alignment = new_shapes[i].alignment
                self.shapes[transition][i].rotate = new_shapes[i].rotate
            elif type(new_shapes[i]) is canvas.Arc:
                self.shapes[transition][i].x = new_shapes[i].x
                self.shapes[transition][i].y = new_shapes[i].y
                self.shapes[transition][i].width = new_shapes[i].width
                self.shapes[transition][i].height = new_shapes[i].height
                self.shapes[transition][i].paint = new_shapes[i].paint
                self.shapes[transition][i].start_angle = new_shapes[i].start_angle
                self.shapes[transition][i].sweep_angle = new_shapes[i].sweep_angle
            elif type(new_shapes[i]) is canvas.Path:
                self.shapes[transition][i].elements = new_shapes[i].elements
                self.shapes[transition][i].paint = new_shapes[i].paint

            self.shapes[transition][i].update()

    def redraw(self):
        self.shapes = {node: self.render_node(node) for node in self.app.graph.nodes}
        self.shapes |= {transition: self.render_transition(transition) for transition in self.app.graph.transitions}
        self.app.ui.drawing_area.shapes = [
            el
            for shape in self.shapes.values()
            for el in shape
        ]
        self.app.ui.drawing_area.update()

    def render_node(self, node: Node):
        elements = []

        match node.type:
            case NodeType.START_FINAL:
                color = self.app.config.start_final_node_color
            case NodeType.START:
                color = self.app.config.start_node_color
            case NodeType.FINAL:
                color = self.app.config.final_node_color
            case _:
                color = self.app.config.node_color

        circle = canvas.Circle(
            x=node.x, y=node.y,
            radius=self.app.config.node_radius,
            paint=ft.Paint(color)
        )
        elements.append(circle)

        if self.app.attr.debug_mode and node.name in self.app.attr.current_states:
            glow = canvas.Circle(
                x=node.x, y=node.y,
                radius=self.app.config.node_radius + 5,
                paint=ft.Paint("#ffff00", style="stroke", stroke_width=4)
            )
            elements.append(glow)

        if self.app.graph.selected_node == node:
            outline = canvas.Circle(
                x=node.x, y=node.y,
                radius=self.app.config.node_radius,
                paint=ft.Paint(self.app.config.selection_color, style="stroke", stroke_width=3)
            )
            elements.append(outline)

        text = canvas.Text(
            x=node.x, y=node.y,
            text=node.name,
            style=TextStyle(weight=FontWeight.BOLD, color=Colors.BLACK),
            alignment=ft.alignment.center
        )
        elements.append(text)

        return elements

    def render_transition(self, transition: Transition):
        elements = []

        start_p = Vector2D.from_node(transition.start)
        end_p = Vector2D.from_node(transition.end)

        is_selected = self.app.graph.selected_transition == transition
        line_color = self.app.config.selection_color if is_selected else "#000000"
        line_width = 3 if is_selected else 2

        if transition.start == transition.end:
            out_phis = {
                Vector2D.from_transition(transition_).phi()
                for transition_ in self.app.graph.transitions
                if transition_.start == transition.start and
                transition_.end != transition.end
            }
            in_phis = {
                (-Vector2D.from_transition(transition_)).phi()
                for transition_ in self.app.graph.transitions
                if transition_.end == transition.end and
                transition_.start != transition.start
            }
            elements += calc_self_line(
                transition.symbols,
                ft.Paint(line_color, stroke_width=line_width),
                start_p,
                self.app.config.node_radius,
                out_phis | in_phis)
            return elements

        double = False
        for transition_ in self.app.graph.transitions:
            if transition_.end == transition.start and transition_.start == transition.end:
                double = True
                break

        if is_line_intersecting_node(start_p, end_p, self.app):
            elements += calc_curved_line(
                transition.symbols,
                ft.Paint(line_color, stroke_width=line_width),
                start_p, end_p,
                self.app.config.node_radius)
        else:
            elements += calc_line(
                transition.symbols,
                ft.Paint(line_color, stroke_width=line_width),
                start_p, end_p,
                double,
                self.app.config.node_radius)

        return elements


def is_line_intersecting_node(start: Vector2D, end: Vector2D, app: Application) -> bool:
    v = end - start
    length = v.length()
    if length == 0:
        return False
    
    dir_norm = v / length
    
    for node in app.graph.nodes:
        p = Vector2D.from_node(node)
        
        if (p - start).length() < 1 or (p - end).length() < 1:
            continue
        
        w = p - start
        t = dot_product(w, dir_norm)
        
        if 0 < t < length:
            dist = (w - dir_norm * t).length()

            if dist < app.config.node_radius + 15:
                return True
                
    return False

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

def calc_curved_line(symbols: str, paint: ft.Paint, start: Vector2D, end: Vector2D, node_radius: float) -> list:
    dir = (end - start).normalized()
    perp = dir.perpendicular()
    
    mid = (start + end) / 2
    control_point = mid - perp * (node_radius * 2.5) 
    
    start_dir = (control_point - start).normalized()
    end_dir = (control_point - end).normalized()
    
    path_start = start + start_dir * node_radius
    path_end = end + end_dir * node_radius

    tangent_dir = (path_end - control_point).normalized()
    arrow_size = 15
    arrow_left = path_end + (tangent_dir * arrow_size).turned(205 * math.pi / 180)
    arrow_right = path_end + (tangent_dir * arrow_size).turned(155 * math.pi / 180)

    text_position = control_point - perp * 10
    text_rotation = dir.phi() + (start.x > end.x) * math.pi

    curve_paint = ft.Paint(paint.color, stroke_width=paint.stroke_width, style=ft.PaintingStyle.STROKE)

    return [
        canvas.Path(
            elements=[
                canvas.Path.MoveTo(path_start.x, path_start.y),
                canvas.Path.QuadraticTo(control_point.x, control_point.y, path_end.x, path_end.y)
            ],
            paint=curve_paint
        ),
        canvas.Line(
            x1=arrow_left.x, y1=arrow_left.y,
            x2=path_end.x, y2=path_end.y,
            paint=paint
        ),
        canvas.Line(
            x1=arrow_right.x, y1=arrow_right.y,
            x2=path_end.x, y2=path_end.y,
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

