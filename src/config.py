from dataclasses import dataclass


@dataclass
class ApplicatonConfig:
    node_radius: int = 30
    transition_arc_radius: int = 25
    selection_color: str = "#4444ff"
    node_color: str = "#ffff44"
    start_node_color: str = "#44ff44"
    final_node_color: str = "#ff4444"
    start_final_node_color: str = "#ff44ff"

