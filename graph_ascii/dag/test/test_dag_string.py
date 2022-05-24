from graph_ascii.dag._string import (
    longest_common_prefix,
    longest_common_suffix,
)


def test_dag_string_longest_common_prefix():
    assert longest_common_prefix(['abc_aaa', 'abc_bb', 'abc_aaaa']) == 'abc_'
    assert longest_common_prefix(['b', 'abc_bb', 'abc_aaaa']) == ''
    assert longest_common_prefix([]) == ''


def test_dag_string_longest_common_suffix():
    assert longest_common_suffix(['abc_aaa', 'abc_bb', 'abc_aaaa']) == ''
    assert longest_common_suffix(['b', 'abc_bb', 'abc_aaaa_bb']) == 'b'
    assert longest_common_suffix(['aaa_bb', 'abc_bb', 'abc_aaaa_bb']) == '_bb'
    assert longest_common_suffix([]) == ''
