from dataclasses import dataclass


@dataclass
class ApplicatonConfig:
    node_radius: int = 30
    transition_arc_radius: int = 25
    selection_color: str = "#333381"
    node_color: str = "#e2e282"
    start_node_color: str = "#75bf75"
    final_node_color: str = "#cf6b6b"
    start_final_node_color: str = "#b97bb9"

