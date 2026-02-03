from dataclasses import dataclass, field
from typing import Set
from enum import Enum


class NodeType(Enum):
    NORMAL = 0
    START = 1
    FINAL = 2
    START_FINAL = 3


@dataclass(unsafe_hash=True)
class Node:
    x: float
    y: float
    name: str
    type: NodeType = NodeType.NORMAL


@dataclass(unsafe_hash=True)
class Transition:
    start: Node
    end: Node
    symbols: str


@dataclass
class Graph:
    nodes: Set[Node] = field(default_factory=set)
    transitions: Set[Transition] = field(default_factory=set)
    node_counter: int = 0
    selected_node: Node = None
    selected_transition: Transition = None
    dragging_node: Node = None

    def get_final_states(self):
        return set(filter(lambda node: node.type in (NodeType.FINAL, NodeType.START_FINAL), self.nodes))

    def get_start_states(self):
        return set(filter(lambda node: node.type in (NodeType.START, NodeType.START_FINAL), self.nodes))
