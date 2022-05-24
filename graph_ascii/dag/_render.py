"""Graph renderer."""
from dataclasses import dataclass
from distutils.sysconfig import customize_compiler
from functools import reduce
from http.client import CannotSendHeader
from itertools import chain
from typing import Any, Dict, Generic, Optional, List, Tuple

from ._collections import group_by_key
from ._graph import Graph
from ._printer import Printer, PrinterOptions
from ._symbol import Symbol, SymbolType
from ._typing import Height, NodeType, RenderedGraph


@dataclass
class Plan(Generic[NodeType]):
    r"""Plan of rendering path nodes and paths at a given height.

    At a given height of the graph, we will have either nodes or
    node paths passing by.

    In the example below, we have L3 at height

    Height  DAG    Label     Nodes     Paths (Nodes By-Passing)
    2       o      L0        L0        -
            |\
    1       o |    L1        L1        L0
            |/
    0       o      L2        L2
    """

    defined: List[NodeType]
    """List of nodes defined at this height."""

    passing_by: List[NodeType]
    """List of nodes of reference that indicate a path that is passing by."""

    __slots__ = ('defined', 'passing_by')


@dataclass
class Cursor(Generic[NodeType]):
    """Path cursors for rendering paths according to the """

    node: NodeType
    """Node of origin for this path cursor."""

    current: int
    """Current position of the cursor."""

    target: int
    """Target position for the cursor."""

    def add(self, delta: int):
        """Return new cursor with current position updated."""
        return Cursor(
            node=self.node,
            current=self.current + delta,
            target=self.target,
        )

    __slots__ = ('node', 'current', 'target')


@dataclass
class Cursors(Generic[NodeType]):

    nodes: List[Cursor[NodeType]]

    paths: List[Cursor[NodeType]]

    __slots__ = ('nodes', 'paths')


@dataclass
class Step(Generic[NodeType]):
    """Intermediary step when moving a cursor."""

    cursor: Cursor[NodeType]
    """Cursor position of the path."""

    symbols: List[Tuple[int, Symbol]]
    """List of symbol and its position in a row."""

    def move_cursor(self, delta: int) -> 'Step[NodeType]':
        """Return new Step with added position to current."""
        return Step(
            cursor=self.cursor.add(delta),
            symbols=self.symbols,
        )

    def add_symbols(
        self, symbols: List[Tuple[int, Symbol]]
    ) -> 'Step[NodeType]':
        """Return new Step with added symbols."""
        return Step(
            cursor=self.cursor,
            symbols=self.symbols + symbols,
        )

    def has_position(self, pos: int) -> bool:
        """Return whether there is a symbol at the queried position."""
        for position, _ in self.symbols:
            if position == pos:
                return True
        return False

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Step):
            return False
        if self.cursor != other.cursor:
            return False
        return set(self.symbols) == set(other.symbols)

    __slots__ = ('cursor', 'symbols')


class Renderer(Generic[NodeType]):
    """Renderer transforms a graph into a string format."""

    def __init__(self,
                 graph: Graph[NodeType],
                 options: PrinterOptions = PrinterOptions()) -> None:
        self.graph = graph
        self.printer = Printer(options=options)

    def to_string(self) -> str:
        """"""
        plan = self._make_plan()
        cursors = self._make_cursors(plan)
        canvas = self._make_canvas(cursors)
        return self.printer.to_string(canvas)

    def _make_plan(self) -> Dict[Height, Plan[NodeType]]:
        height_groups = self.graph.height_groups
        tracking = {
            height: Plan(defined=nodes, passing_by=[])
            for height, nodes in height_groups.items()
        }

        # From the top to the bottom of the graph, compute the paths
        # that are by-passing each level.
        for height in range(max(height_groups), 1, -1):
            self._compute_passing_by(Height(height), tracking)

        return tracking

    def _compute_passing_by(
        self,
        height: Height,
        tracking: Dict[Height, Plan[NodeType]],
    ) -> None:
        # Compute paths by passing a given height level.

        if not (height in tracking and height-1 in tracking):
            return

        current_level = tracking[height]
        next_level = tracking[Height(height-1)]

        for node in current_level.defined:
            for neighbor in self.graph.edges[node]:
                if (self.graph.get_node_height(neighbor) < height
                        and neighbor not in next_level.defined):
                    # Path for (node, neighbor) begins in the current
                    # level but will just passing by over the next.
                    next_level.passing_by.append(node)
                    break

        for node in current_level.passing_by:
            for neighbor in self.graph.edges[node]:
                if (self.graph.get_node_height(neighbor) < height
                        and neighbor not in next_level.defined):
                    # Path for (node, neighbor) is passing by the
                    # current level and will continue passing by over
                    # the next level.
                    next_level.passing_by.append(node)
                    break

    def _make_cursors(self, planning: Dict[Height, Plan[NodeType]]):
        tracking = {}

        for height in range(max(planning), -1, -1):
            height = Height(height)
            if height-1 in planning:
                tracking[height] = self._make_cursor(
                    curr=planning[height],
                    next=planning[Height(height-1)],
                )
            else:
                plan = planning[height]
                nodes = [Cursor(node, i*2, i*2)
                         for i, node in enumerate(plan.defined)]
                n = len(plan.defined)
                paths = [Cursor(node, i*2, i*2)
                         for i, node in enumerate(plan.passing_by, n)]
                tracking[height] = Cursors(nodes, paths)

        return tracking

    def _make_cursor(self,
                     curr: Plan[NodeType],
                     next: Plan[NodeType]) -> Cursors[NodeType]:
        # Return list of new path cursors Cursor(node, current, target).

        # Paths from nodes that are defined in the current level but
        # will be bypassing the next level.
        node_to_passby = []
        for i, node in enumerate(curr.defined):
            j = len(next.passing_by)
            for passby_node in next.passing_by:
                if node == passby_node:
                    node_to_passby.append(Cursor(node, i*2, j*2))
                    break
                j += 1

        # Paths from nodes that are passing by the current level and
        # will continue passing by the next level.
        passby_to_passby = []
        i = len(curr.defined)
        for node in curr.passing_by:
            j = len(next.defined)
            for passby_node in next.passing_by:
                if node == passby_node:
                    passby_to_passby.append(Cursor(node, i*2, j*2))
                    break
                j += 1
            i += 1

        # Paths from nodes that will reach another node in the next level.
        node_to_node = []
        for i, node in enumerate(curr.defined):
            for neighbor in self.graph.edges.get(node, {}):
                for j, next_node in enumerate(next.defined):
                    if neighbor == next_node:
                        node_to_node.append(Cursor(node, i*2, j*2))
                        break

        # Paths from nodes that are by passing the current level but
        # will reach the destination node in the next level.
        passby_to_node = []
        i = len(curr.defined)
        for node in curr.passing_by:
            for neighbor in self.graph.edges.get(node, {}):
                for j, next_node in enumerate(next.defined):
                    if neighbor == next_node:
                        passby_to_node.append(Cursor(node, i*2, j*2))
                        break
            i += 1

        cursors: Cursors[NodeType]
        cursors = Cursors(
            nodes=node_to_node + node_to_passby,
            paths=passby_to_node + passby_to_passby,
        )

        return cursors

    def _make_canvas(self, cursors_mapping: Dict[Height, Cursors]):
        canvas = []
        for height in range(max(cursors_mapping), -1, -1):
            cursors = cursors_mapping[Height(height)]
            canvas.append(self._draw_cursors(cursors))
            canvas.extend(self._draw_paths(cursors.nodes + cursors.paths))
        # The last row always is [HOLD], we discard it.
        canvas.pop()
        return canvas

    def _draw_cursors(self, cursors: Cursors[NodeType]) -> List[Symbol]:
        nodes = {
            cursor.current: Symbol(
                symbol_type=SymbolType.NODE,
                label=self.graph.get_node_label(cursor.node),
            )
            for cursor in cursors.nodes
        }
        paths = {
            cursor.current: Symbol(SymbolType.HOLD)
            for cursor in cursors.paths
        }
        symbols: Dict[int, Symbol] = {}
        symbols.update(nodes)
        symbols.update(paths)

        space = Symbol(SymbolType.SPACE)

        row = []
        for column in range(0, max(symbols)+1):
            row.append(symbols.get(column, space))

        return row

    def _draw_paths(
        self, cursors: List[Cursor[NodeType]]
    ) -> RenderedGraph:
        symbols = self._make_symbols(cursors, [])
        # We may have more than one symbol at a same position, we need
        # to merge those symbols.
        symbol_mappings = [dict(_merge_symbols(row)) for row in symbols]

        space = Symbol(SymbolType.SPACE)

        rows = [
            [
                symbol_mapping.get(column, space)
                for column in range(0, max(symbol_mapping)+1)
            ]
            for symbol_mapping in symbol_mappings
        ]

        return rows

    def _make_symbols(
        self,
        cursors: List[Cursor[NodeType]],
        canvas: List[List[Tuple[int, Symbol]]] = None,
    ) -> List[List[Tuple[int, Symbol]]]:
        # Draw paths getting out of nodes at the current level, each
        # path going to the correct direction.
        no_changes = all(cursor.current == cursor.target
                         for cursor in cursors)
        if no_changes and canvas:
            return canvas

        if canvas is None:
            canvas = []

        steps = self._move_cursors(cursors)
        steps = self._move_left(steps)

        cursors = [step.cursor for step in steps]
        new_symbols = list(chain(*[step.symbols for step in steps]))

        return self._make_symbols(cursors, canvas + [new_symbols])

    def _move_cursors(
            self, cursors: List[Cursor[NodeType]]) -> List[Step[NodeType]]:
        # Move cursors to their directions.
        # The direction is determined by comparison of the current
        # column position and the target column.
        steps = []

        for cursor in cursors:
            if cursor.current < cursor.target:
                # Path goes down to the right.
                # Example:
                # o
                #  \
                steps.append(
                    Step(
                        cursor=cursor.add(delta=2),
                        symbols=[
                            (cursor.current+1, Symbol(SymbolType.RIGHT)),
                        ],
                    )
                )
                continue

            if cursor.current > cursor.target:
                # Path goes down to the left.
                # Example:
                #   o
                #  /
                steps.append(
                    Step(
                        cursor=cursor.add(delta=-2),
                        symbols=[
                            (cursor.current-1, Symbol(SymbolType.LEFT)),
                        ],
                    )
                )
                continue

            # Path goes down straight.
            # Example:
            #  o
            #  |
            steps.append(
                Step(
                    cursor=cursor,
                    symbols=[
                        (cursor.current, Symbol(SymbolType.HOLD)),
                    ],
                )
            )

        return steps

    def _move_left(self, steps: List[Step[NodeType]]):
        new_steps = _move_left(steps)
        while steps != new_steps:
            steps = new_steps
            new_steps = _move_left(steps)
        return new_steps


def _move_left(steps: List[Step[NodeType]]) -> List[Step[NodeType]]:
    new_steps: List[Step[NodeType]] = list()

    for step in steps:
        current = step.cursor.current
        if current <= step.cursor.target:
            new_steps.append(step)
            continue

        # Needs to move to left direction.
        step_curr = _find_step(steps, position=current)
        step_left = _find_step(steps, position=current-1)

        if not step_curr and not step_left:
            # Nothing at current position or current-1 position, so
            # we fill the spaces "  /" as "__/", moving the cursor
            # accordingly.
            new_steps.append(
                step
                .move_cursor(
                    delta=-2
                ).add_symbols([
                    (current-1, Symbol(SymbolType.LEFT_MOVE)),
                    (current, Symbol(SymbolType.LEFT_MOVE)),
                ])
            )
            continue

        if not step_curr and step_left:
            if step_left.cursor.target != step.cursor.target:
                new_steps.append(step)
                continue

            new_steps.append(
                step
                .move_cursor(
                    delta=-2
                ).add_symbols([
                    (current, Symbol(SymbolType.LEFT_MOVE)),
                ])
            )
            continue

        if not step_curr:
            raise RuntimeError('unexpected error')

        if step_curr.cursor.target != step.cursor.target:
            new_steps.append(step)
            continue

        new_steps.append(step.move_cursor(delta=-2))

    return new_steps


def _find_step(
    steps: List[Step[NodeType]],
    position: int,
) -> Optional[Step[NodeType]]:
    # Return the first step with a symbol at a request position.
    for step in steps:
        if step.has_position(position):
            return step
    return None


def _merge_symbols(
    symbols: List[Tuple[int, Symbol]]
) -> List[Tuple[int, Symbol]]:
    return [
        (key, reduce(_resolve_conflict, group))
        for key, group in group_by_key(symbols)
    ]


def _resolve_conflict(a: Symbol, b: Symbol) -> Symbol:
    # Given two symbols a and b at the same position, we return the
    # symbol that represents both at the same time.
    if a.is_node:
        return a
    if b.is_node:
        return b
    if b.is_space:
        return a
    if a.is_space:
        return b
    if a.is_left and b.is_right:
        return Symbol(SymbolType.CROSS)
    if a.is_right and b.is_left:
        return Symbol(SymbolType.CROSS)
    if a.is_cross and (b.is_left or b.is_right):
        return Symbol(SymbolType.CROSS)
    if b.is_cross and (a.is_left or a.is_right):
        return Symbol(SymbolType.CROSS)
    return a
