import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


Point = Tuple[float, float]


@dataclass(frozen=True)
class GeometrySettings:
    node_radius: float
    bidirectional_offset: float
    multi_edge_gap: float
    collision_padding: float
    edge_padding: float = 4.0
    label_push: float = 10.0
    curve_threshold: float = 1.0
    sample_points: int = 24


def iter_transition_metadata(transitions: Dict[str, List[Dict[str, str]]]):
    total_counts = defaultdict(int)
    for start, trans_list in transitions.items():
        for t in trans_list:
            total_counts[(start, t["end"])] += 1

    reverse_exists = {
        key: total_counts.get((key[1], key[0]), 0) > 0
        for key in total_counts
    }

    seen = defaultdict(int)
    for start, trans_list in transitions.items():
        for t in trans_list:
            end = t["end"]
            index = seen[(start, end)]
            seen[(start, end)] += 1
            yield start, t, {
                "index": index,
                "total": total_counts[(start, end)],
                "has_reverse": reverse_exists.get((start, end), False),
            }


def compute_transition_geometry(
    nodes: Dict[str, Point],
    start_name: str,
    end_name: str,
    meta: Dict[str, float],
    settings: GeometrySettings,
):
    if start_name not in nodes or end_name not in nodes:
        return None

    x1, y1 = nodes[start_name]
    x2, y2 = nodes[end_name]
    base_dir, length = _normalize((x2 - x1, y2 - y1))
    if length == 0:
        return None
    ux, uy = base_dir

    canonical_start, canonical_end = sorted((start_name, end_name))
    cx1, cy1 = nodes[canonical_start]
    cx2, cy2 = nodes[canonical_end]
    canonical_dir, canonical_len = _normalize((cx2 - cx1, cy2 - cy1))
    if canonical_len == 0:
        return None
    canonical_perp = (-canonical_dir[1], canonical_dir[0])
    perp = canonical_perp
    direction_sign = 1 if start_name == canonical_start else -1

    radius_with_padding = settings.node_radius + settings.edge_padding
    start_boundary = (x1 + ux * radius_with_padding, y1 + uy * radius_with_padding)
    end_boundary = (x2 - ux * radius_with_padding, y2 - uy * radius_with_padding)

    offset = 0.0
    if meta.get("has_reverse"):
        offset += direction_sign * settings.bidirectional_offset

    total = meta.get("total", 1)
    if total > 1:
        center_index = (total - 1) / 2
        offset += (meta.get("index", 0) - center_index) * settings.multi_edge_gap

    offset = _adjust_offset_for_collisions(
        nodes, start_name, end_name, start_boundary, end_boundary, perp, offset, settings
    )

    mid_x = (start_boundary[0] + end_boundary[0]) / 2
    mid_y = (start_boundary[1] + end_boundary[1]) / 2
    control_x = mid_x + perp[0] * offset
    control_y = mid_y + perp[1] * offset

    start_dir, _ = _normalize((control_x - x1, control_y - y1))
    if start_dir == (0.0, 0.0):
        start_dir = base_dir
    start_x = x1 + start_dir[0] * radius_with_padding
    start_y = y1 + start_dir[1] * radius_with_padding

    end_dir, _ = _normalize((control_x - x2, control_y - y2))
    if end_dir == (0.0, 0.0):
        end_dir = (-base_dir[0], -base_dir[1])
    end_x = x2 + end_dir[0] * radius_with_padding
    end_y = y2 + end_dir[1] * radius_with_padding

    is_curved = abs(offset) > settings.curve_threshold

    points = sample_quadratic_points(
        (start_x, start_y),
        (control_x, control_y),
        (end_x, end_y),
        settings.sample_points,
    )

    arrow_vec = (end_x - control_x, end_y - control_y)
    arrow_dir, arrow_len = _normalize(arrow_vec)
    if arrow_len == 0:
        return None

    label_x, label_y = quadratic_point_at(
        (start_x, start_y), (control_x, control_y), (end_x, end_y), 0.5
    )
    if is_curved:
        label_x += perp[0] * math.copysign(settings.label_push, offset)
        label_y += perp[1] * math.copysign(settings.label_push, offset)

    return {
        "start": (start_x, start_y),
        "end": (end_x, end_y),
        "control": (control_x, control_y),
        "points": points,
        "is_curved": is_curved,
        "arrow_dir": arrow_dir,
        "label": (label_x, label_y),
    }


def sample_quadratic_points(p0: Point, p1: Point, p2: Point, samples: int) -> List[Point]:
    samples = max(2, samples)
    return [quadratic_point_at(p0, p1, p2, i / (samples - 1)) for i in range(samples)]


def quadratic_point_at(p0: Point, p1: Point, p2: Point, t: float) -> Point:
    inv = 1 - t
    x = inv * inv * p0[0] + 2 * inv * t * p1[0] + t * t * p2[0]
    y = inv * inv * p0[1] + 2 * inv * t * p1[1] + t * t * p2[1]
    return (x, y)


def point_to_polyline_distance(px: float, py: float, points: Iterable[Point]) -> float:
    iterator = iter(points)
    try:
        prev = next(iterator)
    except StopIteration:
        return math.inf
    min_distance = math.inf
    for current in iterator:
        min_distance = min(
            min_distance,
            _point_to_segment_distance(px, py, prev[0], prev[1], current[0], current[1]),
        )
        prev = current
    return min_distance


def _adjust_offset_for_collisions(
    nodes: Dict[str, Point],
    start_name: str,
    end_name: str,
    start_pt: Point,
    end_pt: Point,
    perp_vec: Point,
    initial_offset: float,
    settings: GeometrySettings,
):
    offset = initial_offset
    sx, sy = start_pt
    ex, ey = end_pt
    vx, vy = ex - sx, ey - sy
    seg_dir, seg_len = _normalize((vx, vy))
    if seg_len == 0:
        return offset
    ux, uy = seg_dir
    perp_x, perp_y = perp_vec
    threshold = settings.node_radius + settings.edge_padding + settings.collision_padding

    for name, (nx, ny) in nodes.items():
        if name in (start_name, end_name):
            continue
        rel_x = nx - sx
        rel_y = ny - sy
        proj = rel_x * ux + rel_y * uy
        if proj < 0 or proj > seg_len:
            continue
        signed_dist = rel_x * perp_x + rel_y * perp_y
        distance_to_shifted = signed_dist - offset
        if abs(distance_to_shifted) < threshold:
            desired = math.copysign(
                threshold,
                distance_to_shifted if distance_to_shifted != 0 else 1,
            )
            offset = signed_dist - desired
    return offset


def _point_to_segment_distance(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    length_sq = vx * vx + vy * vy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * vx + (py - ay) * vy) / length_sq
    t = max(0.0, min(1.0, t))
    closest_x = ax + t * vx
    closest_y = ay + t * vy
    return math.hypot(px - closest_x, py - closest_y)


def _normalize(vec: Point):
    vx, vy = vec
    length = math.hypot(vx, vy)
    if length == 0:
        return (0.0, 0.0), 0.0
    return (vx / length, vy / length), length
