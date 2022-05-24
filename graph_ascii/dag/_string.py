"""String manipulation algorithms."""
from typing import List


def longest_common_prefix(items: List[str]) -> str:
    """Return the longest common prefix of a list of strings."""
    if not items:
        return ''

    current = items[0]

    for i in range(1, len(items)):
        if not current:
            break

        new_prefix = ''

        for j in range(len(items[i])):
            if j < len(current) and current[j] == items[i][j]:
                new_prefix += current[j]
            else:
                break

        current = new_prefix

    return current


def longest_common_suffix(items: List[str]) -> str:
    """Return the longest common suffix of a list of strings."""
    return longest_common_prefix([item[::-1] for item in items])[::-1]
