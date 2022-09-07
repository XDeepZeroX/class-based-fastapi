import copy
import inspect
import re
import types
from functools import partial
from typing import List, TypeVar, Union

from class_based_fastapi.defaults import GENERIC_ATTRIBUTES
from class_based_fastapi.route_args import RouteArgs

_snake_1 = partial(re.compile(r'(.)((?<![^A-Za-z])[A-Z][a-z]+)').sub, r'\1$*-$%\2')
_snake_2 = partial(re.compile(r'([a-z0-9])([A-Z])').sub, r'\1$*-$%\2')


def snake_case(string: str, separator: str = '-') -> str:
    """Преобразование строки в snake case."""
    case = _snake_2(_snake_1(string)).casefold()
    if separator != '_':
        case = case.replace('$*-$%', separator)
    return case


def find_type_from_getneric(name_param: str, generics: List[dict], raise_exception=True) -> Union[dict, None]:
    type_from_generic = list(filter(lambda x: x['name'] == name_param, generics))
    if len(type_from_generic) > 1 or len(type_from_generic) == 0:
        if raise_exception:
            raise Exception(f'Found -> {len(type_from_generic)} <- generic params')
        return None
    return type_from_generic[0]


def _get_response_type(annotation: type, attrs: List[dict]) -> type:
    if isinstance(annotation, TypeVar):
        # type_from_generic = list(filter(lambda x: x['name'] == annotation.__name__, attrs))
        # if len(type_from_generic) > 1 or len(type_from_generic) == 0:
        #     raise Exception
        type_from_generic = find_type_from_getneric(annotation.__name__, attrs)
        if type_from_generic['type'] is not None:
            annotation = type_from_generic['type']
    elif hasattr(annotation, '__origin__'):
        params = []
        for arg in annotation.__args__:
            type_from_generic = find_type_from_getneric(arg.__name__, attrs, raise_exception=False)
            if type_from_generic is not None and type_from_generic['type'] is not None:
                params.append(type_from_generic['type'])
            else:
                params.append(arg)

        annotation = annotation.__origin__[tuple(params)]

    return annotation


def deepcopy_func(f, args: RouteArgs, cls, name=None):
    clone_func = types.FunctionType(
        f.__code__, f.__globals__, name or f.__name__,
        f.__defaults__, f.__closure__
    )
    new_signature = inspect.signature(clone_func)
    old_signature = inspect.signature(f)
    generics = getattr(cls, GENERIC_ATTRIBUTES, [])
    params = dict(old_signature.parameters.items())
    for name_param, param in new_signature.parameters.items():
        if name_param in params:
            annotation = _get_response_type(params[name_param].annotation, generics)
            # if isinstance(annotation, TypeVar):
            #     type_from_generic = list(filter(lambda x: x['name'] == annotation.__name__, generics))
            #     if len(type_from_generic) > 1 or len(type_from_generic) == 0:
            #         raise Exception
            #     annotation = type_from_generic[0]['type']

            params[name_param] = new_signature.parameters[name_param].replace(annotation=annotation)

    new_signature = new_signature.replace(
        parameters=params.values(),
        return_annotation=_get_response_type(old_signature.return_annotation, generics)
    )
    setattr(clone_func, '__signature__', new_signature)

    if args.response_model is None:
        args.response_model = new_signature.return_annotation
    # inspect.signature(f).parameters['model'].annotation = 123
    attrs_names = [k for k in dir(f) if k not in dir(types.FunctionType)]
    for attr in attrs_names:
        setattr(clone_func, attr, copy.deepcopy(getattr(f, attr)))
    return clone_func
