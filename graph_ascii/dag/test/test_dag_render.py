from dataclasses import dataclass
from functools import partial
from typing import Dict, Final, Generic, List, Tuple

from graph_ascii.dag import Graph, Renderer
from graph_ascii.dag._render import Plan, Cursor, Cursors, Step, _move_left
from graph_ascii.dag._symbol import Symbol, SymbolType
from graph_ascii.dag._typing import Height, NodeType, HeightGroups

from test_dag_graph import sample_graph


def test_dag_render():
    for case in RENDER_TEST_CASES:
        renderer = Renderer(graph=case.graph)

        plan = renderer._make_plan()
        if plan != case.plan:
            print(case.graph)
            print(case.graph.node_heights)

        assert case.graph.height_groups == case.height_groups
        assert plan == case.plan

        cursors = renderer._make_cursors(plan)
        assert cursors == case.cursors

        canvas = renderer._make_canvas(cursors)
        if canvas != case.canvas:
            print('Canvas:', canvas)
            print('Expected Canvas:', case.canvas)

        assert canvas == case.canvas

        assert renderer.to_string() == case.as_string


def test_dag_render_make_symbols():
    for case in MAKE_SYMBOLS_TEST_CASES:
        renderer = Renderer(graph=sample_graph())
        sparse_rendered_paths = renderer._make_symbols(
            cursors=case.cursors,
        )

        result_sets = [set(x) for x in sparse_rendered_paths]
        expected_sets = [set(x) for x in case.symbols]

        if not result_sets == expected_sets:
            print('Case Description:', case.description)
            print('Sparse Rendered Paths:', sparse_rendered_paths)
            print('Expected Rendered Paths:', case.symbols)

        assert result_sets == expected_sets


def test_dag_render_move_left():
    for case in MOVE_LEFT_TEST_CASES:
        new_steps = _move_left(case.steps)

        if not new_steps == case.new_steps:
            print('Case Description:', case.description)
            print('Output Steps:', new_steps)
            print('Expected Steps:', case.new_steps)

        assert new_steps == case.new_steps


@dataclass
class _RenderTestCase(Generic[NodeType]):

    graph: Graph[NodeType]
    """Input graph."""

    height_groups: HeightGroups[NodeType]
    """Expected groups of nodes by height."""

    plan: Dict[Height, Plan]
    """Expected rendering plan."""

    cursors: Dict[Height, Cursors]
    """Expected cursors by height."""

    canvas: List[List[Symbol]]
    """Expected rendered canvas."""

    as_string: str = ''
    """Expected string representation."""


@dataclass
class _MakeSymbolsTestCase(Generic[NodeType]):

    description: str
    """Test case name."""

    cursors: List[Cursor]
    """Input cursor states."""

    symbols: List[List[Tuple[int, Symbol]]]
    """Expected sparse rendered path"""


@dataclass
class _MoveLeftTestCase(Generic[NodeType]):

    description: str
    """Test case description."""

    steps: List[Step[NodeType]]
    """Input steps."""

    new_steps: List[Step[NodeType]]
    """Output steps."""


def description(*args: str) -> str:
    return '\n'.join([*args, ''])


def graph_as_string(*args: str) -> str:
    return '\n'.join([*args, ''])


Node = partial(Symbol, SymbolType.NODE)


CROSS = Symbol(SymbolType.CROSS)
HOLD = Symbol(SymbolType.HOLD)
LEFT = Symbol(SymbolType.LEFT)
LEFT_MOVE = Symbol(SymbolType.LEFT_MOVE)
NODE = Symbol(SymbolType.NODE)
RIGHT = Symbol(SymbolType.RIGHT)
SPACE = Symbol(SymbolType.SPACE)

RENDER_TEST_CASES: Final[List[_RenderTestCase]] = [
    _RenderTestCase(
        graph=Graph(nodes={}, edges={0: {1, 2}, 1: {2}}),
        height_groups={
            Height(2): [0],
            Height(1): [1],
            Height(0): [2],
        },
        plan={
            Height(2): Plan(defined=[0], passing_by=[]),
            Height(1): Plan(defined=[1], passing_by=[0]),
            Height(0): Plan(defined=[2], passing_by=[]),
        },
        cursors={
            Height(2): Cursors(
                nodes=[Cursor(node=0, current=0, target=0),
                       Cursor(node=0, current=0, target=2)],
                paths=[],
            ),
            Height(1): Cursors(
                nodes=[Cursor(node=1, current=0, target=0)],
                paths=[Cursor(node=0, current=2, target=0)],
            ),
            Height(0): Cursors(
                nodes=[Cursor(node=2, current=0, target=0)],
                paths=[],
            ),
        },
        canvas=[
            [NODE],
            [HOLD, RIGHT],
            [NODE, SPACE, HOLD],
            [HOLD, LEFT],
            [NODE],
        ],
        as_string=graph_as_string(
            'o',
            '|\\',
            'o |',
            '|/',
            'o',
        ),
    ),
    _RenderTestCase(
        graph=Graph(nodes={}, edges={0: {1, 3}, 1: {2}, 2: {3}}),
        height_groups={
            Height(3): [0],
            Height(2): [1],
            Height(1): [2],
            Height(0): [3],
        },
        plan={
            Height(3): Plan(defined=[0], passing_by=[]),
            Height(2): Plan(defined=[1], passing_by=[0]),
            Height(1): Plan(defined=[2], passing_by=[0]),
            Height(0): Plan(defined=[3], passing_by=[]),
        },
        cursors={
            Height(3): Cursors(
                nodes=[Cursor(node=0, current=0, target=0),
                       Cursor(node=0, current=0, target=2)],
                paths=[],
            ),
            Height(2): Cursors(
                nodes=[Cursor(node=1, current=0, target=0)],
                paths=[Cursor(node=0, current=2, target=2)],
            ),
            Height(1): Cursors(
                nodes=[Cursor(node=2, current=0, target=0)],
                paths=[Cursor(node=0, current=2, target=0)],
            ),
            Height(0): Cursors(
                nodes=[Cursor(node=3, current=0, target=0)],
                paths=[],
            ),
        },
        canvas=[
            [NODE],
            [HOLD, RIGHT],
            [NODE, SPACE, HOLD],
            [HOLD, SPACE, HOLD],
            [NODE, SPACE, HOLD],
            [HOLD, LEFT],
            [NODE],
        ],
        as_string=graph_as_string(
            'o',
            '|\\',
            'o |',
            '| |',
            'o |',
            '|/',
            'o',
        ),
    ),
    _RenderTestCase(
        graph=Graph(nodes={}, edges={0: {1, 2}, 1: {4}, 2: {3}, 3: {4}}),
        height_groups={
            Height(3): [0],
            Height(2): [2],
            Height(1): [3, 1],
            Height(0): [4],
        },
        plan={
            Height(3): Plan(defined=[0], passing_by=[]),
            Height(2): Plan(defined=[2], passing_by=[0]),
            Height(1): Plan(defined=[3, 1], passing_by=[]),
            Height(0): Plan(defined=[4], passing_by=[]),
        },
        cursors={
            Height(3): Cursors(
                nodes=[Cursor(node=0, current=0, target=0),
                       Cursor(node=0, current=0, target=2)],
                paths=[],
            ),
            Height(2): Cursors(
                nodes=[Cursor(node=2, current=0, target=0)],
                paths=[Cursor(node=0, current=2, target=2)],
            ),
            Height(1): Cursors(
                nodes=[Cursor(node=3, current=0, target=0),
                       Cursor(node=1, current=2, target=0)],
                paths=[],
            ),
            Height(0): Cursors(
                nodes=[Cursor(node=4, current=0, target=0)],
                paths=[],
            ),
        },
        canvas=[
            [NODE],
            [HOLD, RIGHT],
            [NODE, SPACE, HOLD],
            [HOLD, SPACE, HOLD],
            [NODE, SPACE, NODE],
            [HOLD, LEFT],
            [NODE],
        ],
        as_string=graph_as_string(
            'o',
            '|\\',
            'o |',
            '| |',
            'o o',
            '|/',
            'o',
        ),
    ),
    _RenderTestCase(
        graph=sample_graph(),
        height_groups={
            Height(3): [0, 1],
            Height(2): [2, 4, 6, 7],
            Height(1): [3],
            Height(0): [5],
        },
        plan={
            Height(3): Plan(defined=[0, 1], passing_by=[]),
            Height(2): Plan(defined=[2, 4, 6, 7], passing_by=[]),
            Height(1): Plan(defined=[3], passing_by=[]),
            Height(0): Plan(defined=[5], passing_by=[]),
        },
        cursors={
            Height(3): Cursors(
                nodes=[Cursor(node=0, current=0, target=0),
                       Cursor(node=1, current=2, target=0)],
                paths=[]
            ),
            Height(2): Cursors(
                nodes=[Cursor(node=2, current=0, target=0),
                       Cursor(node=4, current=2, target=0),
                       Cursor(node=6, current=4, target=0),
                       Cursor(node=7, current=6, target=0)],
                paths=[]
            ),
            Height(1): Cursors(
                nodes=[Cursor(node=3, current=0, target=0)],
                paths=[]
            ),
            Height(0): Cursors(
                nodes=[Cursor(node=5, current=0, target=0)],
                paths=[]
            ),
        },
        canvas=[
            [Node('L0'), SPACE, Node('L1')],
            [HOLD, LEFT],
            [Node('L2'), SPACE, Node('L4'), SPACE, Node('L6'),
             SPACE, Node('L7')],
            [HOLD, LEFT, LEFT_MOVE, LEFT, LEFT_MOVE, LEFT],
            [Node('L3')],
            [HOLD],
            [Node('L5')]
        ],
        as_string=graph_as_string(
            'o o        L0,L1',
            '|/',
            'o o o o    L2,L4,L6,L7',
            '|/_/_/',
            'o          L3',
            '|',
            'o          L5',
        ),
    ),
]

MAKE_SYMBOLS_TEST_CASES: Final[List[_MakeSymbolsTestCase]] = [
    _MakeSymbolsTestCase(
        description=description(
            'Single node to the right.',
            'Illustration:',
            '01234',
            'o    ',
            ' \\   ',
            '    \\',
        ),
        cursors=[Cursor(node=0, current=0, target=4)],
        symbols=[
            [(1, Symbol(SymbolType.RIGHT))],
            [(3, Symbol(SymbolType.RIGHT))],
        ]
    ),
    _MakeSymbolsTestCase(
        description=description(
            'Single node to the left with left moves.',
            'Illustration:',
            '01234',
            '    o',
            ' __/ ',
        ),
        cursors=[Cursor(node=0, current=4, target=0)],
        symbols=[
            [(1, Symbol(SymbolType.LEFT_MOVE)),
             (2, Symbol(SymbolType.LEFT_MOVE)),
             (3, Symbol(SymbolType.LEFT))],
        ]
    ),
    # Example:
    _MakeSymbolsTestCase(
        description=description(
            'Single node to the left.',
            'Illustration:',
            '01234',
            '  o  ',
            ' /   ',
        ),
        cursors=[Cursor(node=0, current=2, target=0)],
        symbols=[
            [(1, Symbol(SymbolType.LEFT))],
        ]
    ),
    _MakeSymbolsTestCase(
        description=description(
            'Two node paths crossing without a cross symbol.',
            'Illustration:',
            '01234',
            'o   o',
            ' \\ / ',
            ' / \\',
        ),
        cursors=[
            Cursor(node=0, current=0, target=4),
            Cursor(node=0, current=4, target=0),
        ],
        symbols=[
            [(1, Symbol(SymbolType.RIGHT)), (3, Symbol(SymbolType.LEFT))],
            [(1, Symbol(SymbolType.LEFT)), (3, Symbol(SymbolType.RIGHT))],
        ]
    ),
    _MakeSymbolsTestCase(
        description=description(
            'Two node paths cross with a cross symbol',
            'Illustration:',
            '01234',
            'o o  ',
            ' X   ',
            '|  \\',
        ),
        cursors=[
            Cursor(node=0, current=0, target=4),
            Cursor(node=0, current=2, target=0),
        ],
        symbols=[
            [(1, Symbol(SymbolType.RIGHT)), (1, Symbol(SymbolType.LEFT))],
            [(0, Symbol(SymbolType.HOLD)), (3, Symbol(SymbolType.RIGHT))],
        ]
    ),
]

MOVE_LEFT_TEST_CASES: Final[List[_MoveLeftTestCase]] = [
    _MoveLeftTestCase(
        description=description(
            'Three paths, one with left move.',
            'Illustration:',
            '01234',
            '|/_/ ',
        ),
        steps=[
            Step(cursor=Cursor(node=0, current=0, target=0),
                 symbols=[(0, Symbol(SymbolType.HOLD))]),
            Step(cursor=Cursor(node=1, current=0, target=0),
                 symbols=[(1, Symbol(SymbolType.LEFT))]),
            Step(cursor=Cursor(node=2, current=2, target=0),
                 symbols=[(3, Symbol(SymbolType.LEFT))]),
        ],
        new_steps=[
            Step(cursor=Cursor(node=0, current=0, target=0),
                 symbols=[(0, Symbol(SymbolType.HOLD))]),
            Step(cursor=Cursor(node=1, current=0, target=0),
                 symbols=[(1, Symbol(SymbolType.LEFT))]),
            Step(cursor=Cursor(node=2, current=0, target=0),
                 symbols=[(2, Symbol(SymbolType.LEFT_MOVE)),
                          (3, Symbol(SymbolType.LEFT))]),
        ],
    ),
    _MoveLeftTestCase(
        description=description(
            'Three paths, one with left move.',
            'Illustration:',
            '012345',
            '|/_/_/',
        ),
        steps=[
            Step(cursor=Cursor(node=0, current=0, target=0),
                 symbols=[(0, Symbol(SymbolType.HOLD))]),
            Step(cursor=Cursor(node=1, current=0, target=0),
                 symbols=[(1, Symbol(SymbolType.LEFT))]),
            Step(cursor=Cursor(node=2, current=0, target=0),
                 symbols=[(2, Symbol(SymbolType.LEFT_MOVE)),
                          (3, Symbol(SymbolType.LEFT))]),
            Step(cursor=Cursor(node=3, current=2, target=0),
                 symbols=[(4, Symbol(SymbolType.LEFT_MOVE)),
                          (5, Symbol(SymbolType.LEFT))]),
        ],
        new_steps=[
            Step(cursor=Cursor(node=0, current=0, target=0),
                 symbols=[(0, Symbol(SymbolType.HOLD))]),
            Step(cursor=Cursor(node=1, current=0, target=0),
                 symbols=[(1, Symbol(SymbolType.LEFT))]),
            Step(cursor=Cursor(node=2, current=0, target=0),
                 symbols=[(2, Symbol(SymbolType.LEFT_MOVE)),
                          (3, Symbol(SymbolType.LEFT))]),
            Step(cursor=Cursor(node=3, current=0, target=0),
                 symbols=[(4, Symbol(SymbolType.LEFT_MOVE)),
                          (5, Symbol(SymbolType.LEFT))]),
        ],
    ),
    _MoveLeftTestCase(
        description=description(
            'Three paths, one with left move.',
            'Illustration:',
            '01234',
            ' __/  ',
        ),
        steps=[
            Step(cursor=Cursor(node=0, current=2, target=0),
                 symbols=[(3, Symbol(SymbolType.LEFT))]),
        ],
        new_steps=[
            Step(cursor=Cursor(node=0, current=0, target=0),
                 symbols=[(1, Symbol(SymbolType.LEFT_MOVE)),
                          (2, Symbol(SymbolType.LEFT_MOVE)),
                          (3, Symbol(SymbolType.LEFT))]),
        ],
    ),
]
