from dataclasses import dataclass
from typing import Final, List

from graph_ascii.dag._printer import Printer, PrinterOptions, Spacing
from graph_ascii.dag._symbol import Symbol, SymbolType
from graph_ascii.dag._typing import RenderedGraph


def test_dag_printer():
    for case in TEST_CASES:
        p = Printer(options=case.options)
        assert p.to_string(case.rendered_graph) == case.output


@dataclass
class _TestCase:
    rendered_graph: RenderedGraph
    output: str
    options: PrinterOptions = PrinterOptions()


def _output(items: List[str]) -> str:
    return '\n'.join(items) + '\n'


NODE = Symbol(SymbolType.NODE)
HOLD = Symbol(SymbolType.HOLD)
LEFT = Symbol(SymbolType.LEFT)
RIGHT = Symbol(SymbolType.RIGHT)
LEFT_MOVE = Symbol(SymbolType.LEFT_MOVE)
RIGHT_MOVE = Symbol(SymbolType.RIGHT_MOVE)
CROSS = Symbol(SymbolType.CROSS)
SPACE = Symbol(SymbolType.SPACE)

TEST_CASES: Final[List[_TestCase]] = [
    _TestCase(
        rendered_graph=[
            [NODE],
            [HOLD],
            [NODE],
        ],
        output=_output([
            'o',
            '|',
            'o',
        ]),
    ),
    _TestCase(
        rendered_graph=[
            [NODE, SPACE, NODE],
            [HOLD, LEFT],
            [NODE],
        ],
        output=_output([
            'o o',
            '|/',
            'o',
        ]),
    ),
    _TestCase(
        rendered_graph=[
            [NODE],
            [HOLD, RIGHT],
            [NODE, SPACE, HOLD],
            [HOLD, LEFT],
            [NODE],
        ],
        output=_output([
            'o',
            '|\\',
            'o |',
            '|/',
            'o',
        ]),
    ),
    _TestCase(
        rendered_graph=[
            [NODE, SPACE, NODE, SPACE, NODE, SPACE, NODE],
            [HOLD, SPACE, HOLD, LEFT, SPACE, LEFT],
            [NODE, SPACE, CROSS, SPACE, LEFT],
            [HOLD, LEFT, LEFT_MOVE, LEFT],
            [NODE],
        ],
        output=_output([
            'o o o o',
            '| |/ /',
            'o x /',
            '|/_/',
            'o',
        ]),
    ),
    _TestCase(
        rendered_graph=[
            [Symbol(SymbolType.NODE, 'foo-a-bar'),
             SPACE,
             Symbol(SymbolType.NODE, 'foo-b-bar')],
            [HOLD, SPACE, HOLD],
            [Symbol(SymbolType.NODE, 'foo-c-bar1'),
             SPACE,
             Symbol(SymbolType.NODE, 'foo-d-bar2')],
            [HOLD, SPACE, HOLD],
            [Symbol(SymbolType.NODE, '1foo-e-bar'),
             SPACE,
             Symbol(SymbolType.NODE, '2foo-f-bar')],
            [HOLD, SPACE, HOLD],
            [Symbol(SymbolType.NODE, '1foo-g-bar1'),
             SPACE,
             Symbol(SymbolType.NODE, '2foo-h-bar2')],
        ],
        output=_output([
            'o o    foo-{a,b}-bar',
            '| |',
            'o o    foo-{c-bar1,d-bar2}',
            '| |',
            'o o    {1foo-e,2foo-f}-bar',
            '| |',
            'o o    1foo-g-bar1,2foo-h-bar2',
        ]),
    ),
    _TestCase(
        rendered_graph=[
            [Symbol(SymbolType.NODE, 'foo-name'),
             SPACE,
             NODE,
             SPACE,
             Symbol(SymbolType.NODE, 'bar-name'),
             SPACE,
             NODE],
            [HOLD, SPACE, HOLD, LEFT, SPACE, LEFT],
            [Symbol(SymbolType.NODE, 'intermediate-step'),
             SPACE, CROSS, SPACE, LEFT],
            [HOLD, LEFT, LEFT_MOVE, LEFT],
            [Symbol(SymbolType.NODE, 'final-step')],
        ],
        output=_output([
            'o o o o    foo-name,?,bar-name,?',
            '| |/ /',
            'o x /      intermediate-step',
            '|/_/',
            'o          final-step',
        ]),
    ),
    _TestCase(
        rendered_graph=[
            [Symbol(SymbolType.NODE, 'foo-name'),
             SPACE,
             NODE,
             SPACE,
             Symbol(SymbolType.NODE, 'bar-name'),
             SPACE,
             NODE],
            [HOLD, SPACE, HOLD, LEFT, SPACE, LEFT],
            [Symbol(SymbolType.NODE, 'intermediate-step'),
             SPACE, CROSS, SPACE, LEFT],
            [HOLD, LEFT, LEFT_MOVE, LEFT],
            [Symbol(SymbolType.NODE, 'final-step')],
        ],
        output=_output([
            'o o o o foo-name,?,bar-name,?',
            '| |/ /',
            'o x / intermediate-step',
            '|/_/',
            'o   final-step',
        ]),
        options=PrinterOptions(
            spacing=Spacing.JUSTIFIED,
            spaces=4,
        ),
    ),
    _TestCase(
        rendered_graph=[
            [Symbol(SymbolType.NODE, 'foo-name'),
             SPACE,
             NODE,
             SPACE,
             Symbol(SymbolType.NODE, 'bar-name'),
             SPACE,
             NODE],
            [HOLD, SPACE, HOLD, LEFT, SPACE, LEFT],
            [Symbol(SymbolType.NODE, 'intermediate-step'),
             SPACE, CROSS, SPACE, LEFT],
            [HOLD, LEFT, LEFT_MOVE, LEFT],
            [Symbol(SymbolType.NODE, 'final-step')],
        ],
        output=_output([
            'o o o o             foo-name,?,bar-name,?',
            '| |/ /',
            'o x /               intermediate-step',
            '|/_/',
            'o                   final-step',
        ]),
        options=PrinterOptions(
            spacing=Spacing.JUSTIFIED,
            spaces=20,
        ),
    ),
]
