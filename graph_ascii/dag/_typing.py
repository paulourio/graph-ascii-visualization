from typing import Any, Dict, List, NewType, Set, Protocol, TypeVar

from ._symbol import Symbol


class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...


SymbolRow = List[Symbol]
"""Row of symbols, representing a row of a rendered graph."""

RenderedGraph = List[SymbolRow]
"""List of symbol rows."""

NodeType = TypeVar('NodeType', bound=Comparable)
"""Type of a node in a graph."""

Nodes = Dict[NodeType, str]
"""Mapping of a node to its label."""

Edges = Dict[NodeType, Set[NodeType]]
"""Mapping of a node to its set of neighbors."""

Height = NewType('Height', int)

NodeHeights = Dict[NodeType, Height]
"""Mapping of a node to its height."""

HeightGroups = Dict[Height, List[NodeType]]
"""Graph nodes grouped by height."""
