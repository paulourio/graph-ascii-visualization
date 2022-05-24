r"""Test dag module's graph definition.

The sample_graph in these tests is the following:
                              Depth      Height
    o o        L0,L1          0,0        3,3
    |/
    o o o o    L2,L4,L6,L7    1,0,0,0    2,2,2,2
    |/_/_/
    o          L3             2          1
    |
    o          L5             3          0
"""
from random import shuffle
from typing import Iterator, Tuple

from graph_ascii.dag._graph import Graph


def sample_graph() -> Graph[int]:
    return Graph(nodes=SAMPLE_NODES, edges=SAMPLE_EDGES)


def sample_graphs() -> Iterator[Tuple[Graph[int], Graph[int]]]:
    """Generate the same graph shuffling the dictionary ordering."""
    for _ in range(100):
        nodes = list(SAMPLE_NODES.items())
        shuffle(nodes)

        edges = list(SAMPLE_EDGES.items())
        shuffle(edges)

        reverse_edges = list(REVERSE_SAMPLE_EDGES.items())
        shuffle(reverse_edges)

        yield (
            Graph(nodes=dict(nodes), edges=dict(edges)),
            Graph(nodes=dict(nodes), edges=dict(reverse_edges)),
        )


def test_dag_graph():
    for graph, reverse_graph in sample_graphs():
        reverse_graph = graph.reverse_edges()
        assert reverse_graph == reverse_graph

        assert graph.node_heights == NODE_HEIGHTS
        assert reverse_graph.node_heights == REVERSE_NODE_HEIGHTS

        unnamed_graph = Graph(nodes={}, edges=graph.edges)
        assert unnamed_graph.nodes == {i: '' for i in range(8)}

        assert graph.height_groups == HEIGHT_GROUPS


SAMPLE_NODES = {i: f'L{i}' for i in range(8)}

SAMPLE_EDGES = {
    0: {2},
    1: {2},
    2: {3},
    3: {5},
    4: {3},
    6: {3},
    7: {3},
}

REVERSE_SAMPLE_EDGES = {
    2: {0, 1},
    3: {2, 4, 6, 7},
    5: {3},
}

NODE_HEIGHTS = {0: 3, 1: 3, 2: 2, 3: 1, 4: 2, 5: 0, 6: 2, 7: 2}
REVERSE_NODE_HEIGHTS = {0: 0, 1: 0, 2: 1, 3: 2, 4: 0, 5: 3, 6: 0, 7: 0}

HEIGHT_GROUPS = {
    0: [5],
    1: [3],
    2: [2, 4, 6, 7],
    3: [0, 1],
}
