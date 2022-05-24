from collections import defaultdict
import re

import tensorflow as tf

from ._graph import Graph
from ._render import Renderer
from ._typing import Edges, Nodes, NodeType


def render_from_tensorflow_graph(graph: tf.Graph) -> str:
    graph_def = graph.as_graph_def()

    nodes: Nodes[str] = {}
    edges: Edges[str] = defaultdict(set)

    for node in graph_def.node:
        output_name = node.name
        nodes[output_name] = output_name

        for input_full_name in node.input:
            parts = input_full_name.split(':')
            input_name = re.sub(r'^/^', '', parts[0])
            edges[input_name].add(output_name)

    dag = Graph(nodes=nodes, edges=edges)
    renderer = Renderer(graph=dag)

    return renderer.to_string()
