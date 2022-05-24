from collections import defaultdict
from typing import Iterable, List, Tuple, TypeVar


T = TypeVar('T')
Key = TypeVar('Key')
Group = Tuple[Key, T]


def group_by_key(items: Iterable[Tuple[Key, T]]) -> List[Tuple[Key, List[T]]]:
    """Return items grouped by a key.

    Parameters
    ----------
    items : tuple
        List of tuples (key, item) with items to be grouped.
    key : callable
        A callable that returns a comparable element of an item.

    Returns
    -------
    list
        List of tuples (key, items).

    """
    if not items:
        return []

    groups = defaultdict(list)
    for key, item in items:
        groups[key].append(item)

    return list(groups.items())
