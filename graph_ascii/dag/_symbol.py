"""Symbol definitions."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Final


class SymbolType(Enum):
    """SymbolType represents the a unit of information to be output."""

    CROSS = auto()       # Crossing paths.
    HOLD = auto()        # Straight path.
    LEFT = auto()        # Path going down to the left direction.
    LEFT_MOVE = auto()   # Path going to the left at the same level.
    NODE = auto()        # A node in the path.
    RIGHT = auto()       # Path going down to the right direction.
    RIGHT_MOVE = auto()  # Path going to the right at the same level.
    SPACE = auto()       # White space.

    def to_char(self) -> str:
        return _SYMBOL_CHAR[self]


_SYMBOL_CHAR: Final[Dict[SymbolType, str]] = {
    SymbolType.CROSS: 'x',
    SymbolType.HOLD: '|',
    SymbolType.LEFT: '/',
    SymbolType.LEFT_MOVE: '_',
    SymbolType.NODE: 'o',
    SymbolType.RIGHT: '\\',
    SymbolType.RIGHT_MOVE: '_',
    SymbolType.SPACE: ' ',
}


@dataclass
class Symbol:
    """Symbol is a symbol to be output.

    The rendered output is a list of symbols for each row to be printed.
    """

    def __init__(self, symbol_type: SymbolType, label: str = '') -> None:
        self.symbol_type = symbol_type
        self.label = label

    @property
    def is_cross(self) -> bool:
        return self.is_type(SymbolType.CROSS)

    @property
    def is_hold(self) -> bool:
        return self.is_type(SymbolType.HOLD)

    @property
    def is_left(self) -> bool:
        return self.is_type(SymbolType.LEFT)

    @property
    def is_left_move(self) -> bool:
        return self.is_type(SymbolType.LEFT_MOVE)

    @property
    def is_node(self) -> bool:
        return self.is_type(SymbolType.NODE)

    @property
    def is_right(self) -> bool:
        return self.is_type(SymbolType.RIGHT)

    @property
    def is_right_move(self) -> bool:
        return self.is_type(SymbolType.RIGHT_MOVE)

    @property
    def is_space(self) -> bool:
        return self.is_type(SymbolType.SPACE)

    def is_type(self, symbol_type: SymbolType) -> bool:
        return self.symbol_type == symbol_type

    def to_char(self) -> str:
        return self.symbol_type.to_char()

    def __eq__(self, b: object) -> bool:
        if not isinstance(b, Symbol):
            return False
        return self.symbol_type == b.symbol_type and self.label == b.label

    def __hash__(self):
        return hash(self.symbol_type) + hash(self.label)

    def __repr__(self):
        if self.label:
            return f'{self.symbol_type.name}({self.label!r})'
        return self.symbol_type.name

    __slots__ = ('symbol_type', 'label')
