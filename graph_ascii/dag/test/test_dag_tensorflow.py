import tensorflow as tf

from graph_ascii.dag.tensorflow import render_from_tensorflow_graph


def test_dag_tensorflow():
    g = tf.Graph()
    with g.as_default():
        a = tf.constant(1, name='a')
        b = tf.constant(2, name='b')
        _ = tf.add(a, b, name='c')

    output = render_from_tensorflow_graph(g)

    assert output == _EXPECTED


_EXPECTED = '\n'.join([
    'o o    a,b',
    '|/',
    'o      c',
    '',
])
