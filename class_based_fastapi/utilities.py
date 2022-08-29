import re
from functools import partial

_snake_1 = partial(re.compile(r'(.)((?<![^A-Za-z])[A-Z][a-z]+)').sub, r'\1$*-$%\2')
_snake_2 = partial(re.compile(r'([a-z0-9])([A-Z])').sub, r'\1$*-$%\2')


def snake_case(string: str, separator: str = '-') -> str:
    """Преобразование строки в snake case."""
    case = _snake_2(_snake_1(string)).casefold()
    if separator != '_':
        case = case.replace('$*-$%', separator)
    return case
