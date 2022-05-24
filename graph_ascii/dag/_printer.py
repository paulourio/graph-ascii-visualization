"""Printer implementation."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple

from ._typing import RenderedGraph, SymbolRow
from ._string import longest_common_prefix, longest_common_suffix


class Spacing(Enum):
    """Spacing method to separate the DAG from the labels."""

    FIXED = auto()
    """Always print a fixed number of spaces before printing labels."""

    JUSTIFIED = auto()
    """Align labels at a specified column."""

    AUTO_JUSTIFIED = auto()
    """Align labels automatically so that all labels are aligned."""


@dataclass
class PrinterOptions:

    spacing: Spacing = Spacing.AUTO_JUSTIFIED
    """Spacing method for separating the nodes from their labels.
    If you plan using for versioning DAGs, setting to fixed spacing
    should be more appropiate."""

    spaces: int = 4
    """Number of spaces.

    When spacing is fixed, this is the number of spaces to always print
    before printing the label names.

    When spacing is justified, this is the minimum column to which
    labels will be aligned.

    When spacing is auto-justified, this parameter is the minimum
    distance between the DAG and the labels.
    """

    group_labels_by_prefix: bool = True
    """Whether two labels in the same row should be grouped.

    When enabled, `label-foo,label-bar` becomes `label-{foo,bar}`.
    """

    group_labels_by_suffix: bool = True
    """Whether two labels in the same row should be grouped.

    When enabled, `foo-suffix,bar-suffix` becomes `{foo,bar}-suffix`.
    """

    min_group_size: int = 2
    """Minimum number of labels in the same row to allow grouping."""

    prefix_min_length: int = 4
    """Minimum length for a common prefix to be grouped."""

    suffix_min_length: int = 4
    """Minimum lengeth for a common suffix to be grouped."""


class Printer:

    def __init__(self, options: PrinterOptions = PrinterOptions()) -> None:
        self.options = options

    def to_string(self, rendered_graph: RenderedGraph) -> str:
        """Return the ASCII formatted representation of a rendered graph.

        Parameters
        ----------
        rendered_graph: list of symbol rows
            A list of rows, where each row is a sequence of symbols to
            be printed.

        """
        max_size = max(len(row) for row in rendered_graph)
        return '\n'.join(_RowPrinter(row, max_size, self.options).to_string()
                         for row in rendered_graph) + '\n'


class _RowPrinter:
    # Helper class for printing a single row.

    def __init__(self, row: SymbolRow, max_size: int,
                 options: PrinterOptions) -> None:
        self.row = row
        self.options = options
        self.output: List[str] = []
        self.labels: List[str] = []
        self.max_size = max_size
        if options.spacing == Spacing.FIXED:
            self._print_spacing = self._print_fixed_spacing
        elif options.spacing == Spacing.JUSTIFIED:
            self._print_spacing = self._print_justified_spacing
        elif options.spacing == Spacing.AUTO_JUSTIFIED:
            self._print_spacing = self._print_auto_justified_spacing
        else:
            raise ValueError('unknown spacing method')

    def to_string(self) -> str:
        self._print_symbols()

        if self.labels and max([len(label) for label in self.labels]) > 0:
            # At least one of symbol nodes have labels.
            self._print_spacing()
            self._print_labels()

        return ''.join(self.output)

    def _print_symbols(self):
        for symbol in self.row:
            if symbol.is_node:
                self.labels.append(symbol.label)
            self.output.append(symbol.to_char())

    def _print_fixed_spacing(self):
        self.output.append(' ' * self.options.spaces)

    def _print_justified_spacing(self):
        used_chars = sum(len(w) for w in self.output)
        if used_chars == 0:
            return

        needed_spaces = self.options.spaces - used_chars

        self.output.append(' ' * max(1, needed_spaces))

    def _print_auto_justified_spacing(self):
        used_chars = sum(len(w) for w in self.output)
        if used_chars == 0:
            return

        alignment = self.max_size + self.options.spaces
        needed_spaces = alignment - used_chars

        self.output.append(' ' * max(0, needed_spaces))

    def _print_labels(self):
        prefix, labels = self._maybe_group_by_prefix(self.labels)
        labels, suffix = self._maybe_group_by_suffix(labels)
        fmt_labels = ','.join([name if name else '?' for name in labels])

        if prefix or suffix:
            self.output.append(f'{prefix}{{{fmt_labels}}}{suffix}')
        else:
            self.output.append(fmt_labels)

    def _maybe_group_by_prefix(self, labels) -> Tuple[str, List[str]]:
        # Group `prefix-foo,prefix-bar` as `prefix-{foo,bar}`.
        # Returns (prefix, labels)
        if not (self.options.group_labels_by_prefix
                and len(self.labels) >= self.options.min_group_size):
            return ('', labels)

        prefix = longest_common_prefix(labels)

        prefix_len = len(prefix)
        if prefix_len < self.options.prefix_min_length:
            return ('', labels)

        return (prefix, [label[prefix_len:] for label in labels])

    def _maybe_group_by_suffix(self, labels) -> Tuple[List[str], str]:
        if not (self.options.group_labels_by_suffix
                and len(self.labels) >= self.options.min_group_size):
            return (labels, '')

        suffix = longest_common_suffix(labels)

        suffix_len = len(suffix)
        if suffix_len < self.options.suffix_min_length:
            return (labels, '')

        return ([label[:-suffix_len] for label in labels], suffix)
