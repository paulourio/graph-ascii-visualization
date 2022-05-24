"""Graph definition for DAG rendering."""
from collections import defaultdict
from functools import cached_property
from typing import Generic, List, Tuple

from ._collections import group_by_key
from ._typing import (
    Edges,
    Height,
    HeightGroups,
    NodeHeights,
    Nodes,
    NodeType,
)


class Graph(Generic[NodeType]):
    """Direct graph representation.

    This graph is used exclusively for rendering.

    Parameters
    ----------
    nodes : dict
        Mapping of node and its label string.
    edges : dict
        Mapping of node to its set of neighbor nodes.

    """

    def __init__(self, nodes: Nodes[NodeType],
                 edges: Edges[NodeType]) -> None:
        self.nodes = nodes
        self.edges = edges
        self._init_nodes()

    @cached_property
    def node_heights(self) -> NodeHeights[NodeType]:
        mapping: NodeHeights[NodeType] = {}
        for node in self.nodes:
            self._node_height(mapping, node)
        return mapping

    @cached_property
    def height_groups(self) -> HeightGroups[NodeType]:
        heights = self.node_heights
        reverse_heights = self.reverse_edges().node_heights

        def score(node: NodeType) -> int:
            return heights.get(node, 0) + reverse_heights.get(node, 0)

        def sorted_group(nodes: List[NodeType]) -> List[NodeType]:
            return sorted(
                nodes,
                key=lambda node: (-score(node), self.get_node_label(node)),
            )

        # Group nodes by height.
        groupings = group_by_key((height, node)
                                 for node, height in heights.items())

        # Within each height, sort by reverse heights.
        height_groups = {
            height: sorted_group(group)
            for height, group in groupings
        }

        return height_groups

    def has_edge(self, pair: Tuple[NodeType, NodeType]) -> bool:
        return pair[1] in self.edges.get(pair[0], {})

    def get_node_label(self, node: NodeType) -> str:
        return self.nodes[node]

    def get_node_height(self, node: NodeType) -> Height:
        return self.node_heights[node]

    def reverse_edges(self) -> 'Graph[NodeType]':
        """Return a graph with reversed edges."""
        edges = defaultdict(set)
        for src, destinations in self.edges.items():
            for dest in destinations:
                edges[dest].add(src)
        return Graph(nodes=self.nodes, edges=dict(edges))

    def _init_nodes(self):
        # We may not have received all nodes, add empty node labels.
        for src, neighbors in self.edges.items():
            if src not in self.nodes:
                self.nodes[src] = ''
            for neighbor in neighbors:
                if neighbor not in self.nodes:
                    self.nodes[neighbor] = ''

    def _node_height(self, mapping: NodeHeights[NodeType],
                     node: NodeType, depth: int = 0) -> Height:
        # Return the node's height in this graph.
        #
        # The node's height equals to the longest path we can walk
        # starting from the node.
        #
        # This method changes argument mapping to update the walk over
        # the graph, and return the node's height.
        if node in mapping:
            return mapping[node]

        height = 0
        if node in self.edges:
            height = 1 + max(self._node_height(mapping, neighbor,
                                               depth=depth+1)
                             for neighbor in self.edges[node])

        mapping[node] = Height(height)
        return Height(height)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Graph):
            return False
        return other.edges == self.edges and other.nodes == self.nodes

    def __repr__(self) -> str:
        return f'Graph(nodes={self.nodes!r}, edges={self.edges!r})'
