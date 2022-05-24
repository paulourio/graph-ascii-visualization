from typing import Final, List
import os

from graph_ascii.dag.graphviz import render_from_dot_filename


def test_dag_graphviz():
    for case in GRAPHVIZ_TEST_CASES:
        assert render_from_dot_filename(case.input) == case.output_content


class GraphvizTestCase:

    def __init__(self, name: str, input: str, output: str) -> None:
        dirname = os.path.dirname(__file__)
        self.name = name
        self.input = os.path.join(dirname, input)
        self.output = os.path.join(dirname, output)
        self.output_content = open(self.output, 'rt').read()


GRAPHVIZ_TEST_CASES: Final[List[GraphvizTestCase]] = [
    GraphvizTestCase(
        name='Case 1',
        input='data/test.dot',
        output='data/test.txt',
    ),
    GraphvizTestCase(
        name='Pseudo Inception',
        input='data/pseudo_inception.dot',
        output='data/pseudo_inception.txt',
    ),
    GraphvizTestCase(
        name='Inception V3',
        input='data/inception_v3.dot',
        output='data/inception_v3.txt',
    ),
]
