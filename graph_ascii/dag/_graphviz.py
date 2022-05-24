"""Graph rendering for Graphviz's DOT file and pydot."""
from collections import defaultdict
from typing import Dict, IO, Set
import logging

import pydot

from ._graph import Graph
from ._render import Renderer
from ._typing import Edges, Nodes, NodeType


def render_from_dot_filename(filename: str) -> str:
    """Render a DAG from an input in Graphviz's DOT format.

    Parameters
    ----------
    filename : str
        The filename of a DOT file to be read.

    Returns
    -------
    str
        The string representation of the graph.

    """
    with open(filename, 'rt') as dot_file:
        return render_from_dot_file(dot_file)


def render_from_dot_file(input: IO) -> str:
    """Render a DAG from an input in Graphviz's DOT format.

    Parameters
    ----------
    input :file-like
        A file-like object from which the graph will be read.

    Returns
    -------
    str
        The string representation of the graph.

    """
    graphs = pydot.graph_from_dot_data(input.read())
    if len(graphs) != 1:
        _LOGGER.warning(
            'Read %d graphs from a DOT file, rendering only the first.',
            len(graphs))
    return render_from_dot_graph(graphs[0])


def render_from_dot_graph(graph: pydot.Dot) -> str:
    nodes: Nodes[str] = {}
    for node in graph.get_nodes():
        attrs = node.get_attributes()
        if 'label' in attrs:
            name = node.get_name()
            label = attrs['label'].strip('"')
            nodes[name] = label

    edges: Edges[str] = defaultdict(set)
    for edge in graph.get_edges():
        source = edge.get_source()
        destination = edge.get_destination()
        edges[source].add(destination)

    dag = Graph(nodes=nodes, edges=dict(edges))
    renderer = Renderer(dag)
    return renderer.to_string()


_LOGGER = logging.getLogger(__name__)
