import copy
import re
import types
from functools import partial

_snake_1 = partial(re.compile(r'(.)((?<![^A-Za-z])[A-Z][a-z]+)').sub, r'\1$*-$%\2')
_snake_2 = partial(re.compile(r'([a-z0-9])([A-Z])').sub, r'\1$*-$%\2')


def snake_case(string: str, separator: str = '-') -> str:
    """Преобразование строки в snake case."""
    case = _snake_2(_snake_1(string)).casefold()
    if separator != '_':
        case = case.replace('$*-$%', separator)
    return case


def deepcopy_func(f, name=None):
    clone_func = types.FunctionType(
        f.__code__, f.__globals__, name or f.__name__,
        f.__defaults__, f.__closure__
    )
    attrs_names = [k for k in dir(f) if k not in dir(types.FunctionType)]
    for attr in attrs_names:
        setattr(clone_func, attr, copy.deepcopy(getattr(f, attr)))
    return clone_func
