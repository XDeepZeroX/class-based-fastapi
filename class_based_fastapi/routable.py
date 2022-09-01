import copy
import dataclasses
import inspect
from functools import partial
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar, cast

from fastapi.routing import APIRouter

from .route_args import EndpointDefinition
from .templates_formatting import _rest_api_naming, _processing_child_paths

AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])


class RoutableMeta(type):
    """This is a meta-class that converts all the methods that were marked by a route/path decorator into values on a
    class member called _endpoints that the Routable constructor then uses to add the endpoints to its router."""

    @staticmethod
    def _compute_path(endpoint: EndpointDefinition, name: str, bases: Tuple[Type[Any]], attrs: Dict[str, Any]) -> str:
        """Формирование шаблона URI

        Args:
            endpoint: Информация о методе
            name: Название контроллера
            bases: Дочерние типы
            attrs: Атрибуты

        Returns: Сформированный шаблон URI
        """
        template = endpoint.args.path

        base_template = bases[0].BASE_TEMPLATE_PATH
        if not str.startswith(template, '/'):
            template = base_template.replace('{user_path}', template)

        name_module = attrs.get('NAME_MODULE', '') or bases[0].NAME_MODULE
        if '{module}' in template and (name_module is None or name_module == ''):
            template = template.replace('/{module}', '')

        # Template
        if str.endswith(template, '/'):
            template = template[:-1]
        endpoint.args.template_path = template

        # Name module
        name_module = _rest_api_naming(name_module)
        endpoint.args.name_module = name_module

        # Version
        varsion_api = str.lower(attrs.get('VERSION_API') or bases[0].VERSION_API)
        endpoint.args.varsion_api = varsion_api

        # Replacement
        path = template \
            .replace('{module}', name_module) \
            .replace('{version}', varsion_api) \
            .replace('{controller}', _rest_api_naming(name))
        return path

    def __new__(cls: Type[type], name: str, bases: Tuple[Type[Any]], attrs: Dict[str, Any]) -> 'RoutableMeta':
        endpoints: dict[str, EndpointDefinition] = {}
        for v in attrs.values():
            if inspect.isfunction(v) and hasattr(v, '_endpoint'):
                # endpoints.append(v._endpoint)
                # pass

                path = cls._compute_path(v._endpoint, name, bases, attrs)
                v._endpoint.args.path = path
                # v._endpoint.args.path \
                # .replace('{module}', bases[0].NAME_MODULE) \
                # .replace('{version}', bases[0].VERSION_API) \
                # .replace('{controller}', name)

                endpoints[v.__name__] = v._endpoint

        base_endpoints = {}
        for base in bases:
            _endpoints = getattr(base, '_endpoints')
            if isinstance(_endpoints, dict):
                base_endpoints.update(copy.deepcopy(_endpoints))

        attrs['_endpoints'] = _processing_child_paths({**base_endpoints, **endpoints}, name, bases, attrs)

        # for endpoint in attrs['_endpoints'].values():
        #     print(endpoint.args.path)

        return cast(RoutableMeta, type.__new__(cls, name, bases, attrs))


class Routable(metaclass=RoutableMeta):
    """Base class for all classes the want class-based routing.

    This Uses RoutableMeta as a metaclass and various decorators like @get or @post from the decorators module. The
    decorators just mark a method as an endpoint. The RoutableMeta then converts those to a list of desired endpoints in
    the _endpoints class method during class creation. The constructor constructs an APIRouter and adds all the routes
    in the _endpoints to it so they can be added to an app via FastAPI.include_router or similar.
    """
    _endpoints: List[EndpointDefinition] = []
    VERSION_API = '1.0'
    NAME_MODULE = ''

    BASE_TEMPLATE_PATH = '/{module}/{controller}/v{version}/{user_path}'

    def __init__(self) -> None:

        # self.VERSION_API = '1.0'
        # self.NAME_MODULE = ''
        #
        # self.BASE_TEMPLATE_PATH = '/{module}/{controller}/v{version}/{user_path}'

        self.router = APIRouter()
        for endpoint in self._endpoints.values():
            self.router.add_api_route(
                endpoint=partial(endpoint.endpoint, self),
                **dataclasses.asdict(endpoint.args)
            )
