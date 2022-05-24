from typing import Final, List, Tuple

from graph_ascii.dag._collections import group_by_key


def test_dag_group_by_key():
    for items, expected_groups in TEST_GROUP_BY_KEY:
        assert group_by_key(items) == expected_groups


TEST_GROUP_BY_KEY: Final[List[Tuple[List, List]]] = [
    ([], []),
    (
        [
            (2, 0),
            (2, 1),
            (3, 2),
            (3, 4),
            (3, 6),
            (5, 3),
        ],
        [
            (2, [0, 1]),
            (3, [2, 4, 6]),
            (5, [3]),
        ],
    ),
]
