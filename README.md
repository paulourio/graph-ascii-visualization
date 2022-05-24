# Graph Visualization in ASCII

I use this module for inspecting graphs in text format.
I have only implemented for direct acyclic graphs for now.
The ASCII format allows to easily print DAGs for logging and versioning, without requiring matplotlib, networkx or any other large lib.

This project is based on Junji Hashimoto's rendering algorithm I found in `stacked-dag`.

## Printing Direct Acyclic Graphs (DAGs) in ASCII

You may use the internal API or one of `graph_ascii.dag.graphviz` or `graph_ascii.dag.tensorflow`.

### API Usage

Construct a DAG with `graph_ascii.dag.Graph(node_labels, edge_sets)`, and then use `graph_ascii.dag.Renderer` to render the graph in ASCII:

```python
import graph_ascii

g = graph_ascii.dag.Graph(
    nodes={i: f'Node{i}' for i in range(8)},
    edges={0: {2}, 1: {2}, 2: {3}, 3: {5}, 4: {3}, 6: {3}, 7: {3}}
)
print(graph_ascii.dag.Renderer(g).to_string())
```
Output:

```
o o        Node{0,1}
|/
o o o o    Node{2,4,6,7}
|/_/_/
o          Node3
|
o          Node5
```

Use `graph_ascii.dag.PrinteOptions` to configure how you want the renderer to generate the graph in ASCII.
The example below is the same graph from above but we change a few settings:

```python
import graph_ascii

g = graph_ascii.dag.Graph(
    nodes={i: f'Node{i}' for i in range(8)},
    edges={0: {2}, 1: {2}, 2: {3}, 3: {5}, 4: {3}, 6: {3}, 7: {3}}
)
opts = graph_ascii.dag.PrinterOptions(
    spacing=graph_ascii.dag.Spacing.FIXED,
    spaces=10,
    group_labels_by_prefix=False,
)
print(graph_ascii.dag.Renderer(g, opts).to_string())
```
Output:

```
o o          Node0,Node1
|/
o o o o          Node2,Node4,Node6,Node7
|/_/_/
o          Node3
|
o          Node5
```
## Rendering tensorflow graphs

Tensorflow module is not loaded automatically, thus you need to import it directly.

```python
from graph_ascii.dag.tensorflow import render_from_tensorflow_graph
import tensorflow as tf

g = tf.Graph()
with g.as_default():
    a = tf.constant(1, name='a')
    b = tf.constant(2, name='b')
    _ = tf.add(a, b, name='c')

render_from_tensorflow_graph(g)
```
Output:
```
o o    a,b
|/
o      c
```

## Rendering Graphviz DOT graphs

Graphviz module is not loaded automatically, thus you need to import it directly.

```python
from graph_ascii.dag.graphviz import render_from_dot_filename

print(render_from_dot_filename('graph_ascii/dag/test/data/test.dot'))
```
Output:
```
o
|
o
|\
o |
| |\
o o |
|\ \ \
| | |\ \
| | | | |\
o o o o o |
|/ /_/ / /
| |  / /
o o o o
|/_/_/
o
```
