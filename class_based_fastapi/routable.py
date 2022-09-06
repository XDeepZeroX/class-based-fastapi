import copy
import dataclasses
import inspect
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar, cast, get_type_hints

from fastapi import Depends, APIRouter
from pydantic.typing import is_classvar

from .decorators import CONTROLLER_METHOD_KEY
from .templates_formatting import _rest_api_naming
from .utilities import deepcopy_func

AnyCallable = TypeVar('AnyCallable', bound=Callable[..., Any])

CBV_CLASS_KEY = "__cbv_class__"
CLASS_TYPE = "__cbv_class__"

SIGNATURE_KEY = "__signature__"
API_METHODS = "__api_methods__"
INIT_MODIFIED = "__init_modified__"


class RoutableMeta(type):
    """Это метакласс, который формирует методы API, которые были отмечены декоратором маршрута/пути, в значения
    для конструктора маршрутизации добавления конечных точек к своему маршрутизатору из библиотеки FastAPI."""

    __inheritors__ = defaultdict(list)
    __inheritors_set__ = set()

    @staticmethod
    def get_config_endpoints(bases: Tuple[Type[Any]], attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Получение конфигурации всех методов API

        Args:
            bases: Дочерние типы
            attrs: Атрибуты класса

        Returns: Конфигурация всех методов API

        """
        cls_ = attrs.get(CLASS_TYPE)
        if cls_ is None:
            return {}

        new_methods = list(filter(lambda x: hasattr(x[1], CONTROLLER_METHOD_KEY), attrs.items()))
        old_methods = attrs.get(API_METHODS, dict())
        if not len(old_methods) and len(bases):
            old_methods = {}
            for base in bases:
                if not hasattr(base, API_METHODS):
                    continue
                for name_method, args in getattr(base, API_METHODS).items():
                    old_methods[name_method] = copy.deepcopy(args)

        for name_method, endpoint in new_methods:
            old_methods[name_method] = copy.deepcopy(endpoint._endpoint.args)

        return copy.deepcopy(old_methods)

    @staticmethod
    def _init_cbv(cls: Type[type]) -> None:
        """Идемпотентно изменяет предоставленный "cls", выполняя следующие модификации:

        * Функция `__init__` обновлена для установки любых зависимостей с аннотациями к классу в качестве атрибутов экземпляра.
        * Атрибут `__signature__` обновляется, чтобы указать FastAPI, какие аргументы следует передавать инициализатору

        Args:
            cls: Тип модифицируемого класса

        Returns: None
        """
        old_init: Callable[..., Any] = cls.__init__
        if getattr(old_init, INIT_MODIFIED, False):
            return
        old_signature = inspect.signature(old_init)
        old_parameters = list(old_signature.parameters.values())[1:]  # drop `self` parameter
        new_parameters = [
            x for x in old_parameters if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        dependency_names: List[str] = []
        for name, hint in get_type_hints(cls).items():
            if is_classvar(hint) or name == '_endpoints':
                continue
            parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
            dependency_names.append(name)
            new_parameters.append(
                inspect.Parameter(name=name, kind=inspect.Parameter.KEYWORD_ONLY, annotation=hint, **parameter_kwargs)
            )
        new_signature = old_signature.replace(parameters=new_parameters)

        def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
            for dep_name in dependency_names:
                try:
                    dep_value = kwargs.pop(dep_name)
                    setattr(self, dep_name, dep_value)
                except Exception as ex:
                    print(ex)
                    pass
            old_init(self, *args, **kwargs)

        setattr(new_init, INIT_MODIFIED, True)
        setattr(cls, "__signature__", new_signature)
        setattr(cls, "__init__", new_init)

        # attrs["__signature__"] = new_signature
        # attrs["__init__"] = new_init
        # attrs[CBV_CLASS_KEY] = True

    @staticmethod
    def __new_instance__(cls: Type[type], name: str, bases: Tuple[Type[Any]], attrs: Dict[str, Any]) -> 'RoutableMeta':
        """Создание нового типа и запоминание родительских типов

        Args:
            cls: Исходный тип (родительский)
            name: Название создаваемого типа
            bases: Родительские типы
            attrs: Атрибуты создаваемого типа

        Returns: Созданный тип
        """
        # Унаследованные классы
        klass = cast(RoutableMeta, type.__new__(cls, name, bases, attrs))
        for base in klass.mro()[1:-1]:
            cls.__inheritors__[base].append(klass)
            cls.__inheritors_set__.add(klass)
        return klass

    @staticmethod
    def get_type_instance(cls: Type[type], name: str):
        """Получение типа, наследующегося от cls

        Args:
            cls: Родительский тип
            name: Название дочернего типа

        Returns: Унаследованный тип, соответствующий названию name

        """
        for class_ in cls.__inheritors_set__:
            if class_.__name__ == name:
                return class_

    @staticmethod
    def _compute_path_new(cls: Type[type], func: Callable) -> Callable:
        """Формирование шаблона URI

       Args:
           cls: Тип класса
           func: Метод API

       Returns: Сформированный метод API
       """
        func_ = deepcopy_func(func)

        config_methods = getattr(cls, API_METHODS)
        args = config_methods[func_.__name__] if func_.__name__ in config_methods else func_._endpoint.args
        user_path = args.path
        base_template = cls.BASE_TEMPLATE_PATH
        if not str.startswith(user_path, '/'):
            user_path = base_template.replace('{user_path}', user_path)

        name_module = cls.NAME_MODULE
        if '{module}' in user_path and (name_module is None or name_module == ''):
            user_path = user_path.replace('/{module}', '')

        # Template
        if str.endswith(user_path, '/'):
            user_path = user_path[:-1]
        args.template_path = user_path

        # Name module
        name_module = _rest_api_naming(name_module)
        args.name_module = name_module

        # Version
        varsion_api = str.lower(cls.VERSION_API)
        args.varsion_api = varsion_api

        # Replacement
        path = user_path \
            .replace('{module}', name_module) \
            .replace('{version}', varsion_api) \
            .replace('{controller}', _rest_api_naming(cls.__name__))
        args.path = path
        # print(f'{args.methods}: {path}')
        return func_

    @staticmethod
    def get_router(cls: Type[type]) -> APIRouter:
        """Формирование функции возвращающей маршруты API

        Args:
            cls: Тип класса, содержащий методы API

        Returns: APIRouter
        """
        config_methods = getattr(cls, API_METHODS)
        functions = [
            RoutableMeta._compute_path_new(cls, func)
            for name, func in inspect.getmembers(cls, inspect.isfunction)
            if hasattr(func, CONTROLLER_METHOD_KEY) or name in config_methods
        ]

        router = APIRouter()

        for endpoint in functions:
            # get the signature of the endpoint function
            signature = inspect.signature(endpoint)
            # get the parameters of the endpoint function
            signature_parameters = list(signature.parameters.values())

            # replace the class instance with the itself FastApi Dependecy
            signature_parameters[0] = signature_parameters[0].replace(
                default=Depends(cls)
            )

            # set self and after it the keyword args
            new_parameters = [signature_parameters[0]] + [
                parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
                for parameter in signature_parameters[1:]
            ]

            new_signature = signature.replace(parameters=new_parameters)
            setattr(endpoint, SIGNATURE_KEY, new_signature)

            args = config_methods[endpoint.__name__] if endpoint.__name__ in config_methods else endpoint._endpoint.args
            router.add_api_route(
                endpoint=endpoint,
                **dataclasses.asdict(args)
            )
        return router

    def __new__(cls: Type[type], name: str, bases: Tuple[Type[Any]], attrs: Dict[str, Any]) -> 'RoutableMeta':
        RoutableMeta.__new_instance__(cls, name, bases, attrs)
        cls_ = RoutableMeta.get_type_instance(cls, name)
        attrs[CLASS_TYPE] = cls_

        if cls_ is not None:
            methods = RoutableMeta.get_config_endpoints(bases, attrs)
            setattr(cls_, API_METHODS, methods)
            attrs[API_METHODS] = methods

        attrs['routes'] = lambda: RoutableMeta.get_router(RoutableMeta.get_type_instance(cls, name))

        # RoutableMeta.signature(cls, name, bases, attrs)
        if cls_ is not None:
            RoutableMeta._init_cbv(cls_)

        return cast(RoutableMeta, type.__new__(cls, name, bases, attrs))


class Routable(metaclass=RoutableMeta):
    """Base class for all classes the want class-based routing.

    This Uses RoutableMeta as a metaclass and various decorators like @get or @post from the decorators module. The
    decorators just mark a method as an endpoint. The RoutableMeta then converts those to a list of desired endpoints in
    the _endpoints class method during class creation. The constructor constructs an APIRouter and adds all the routes
    in the _endpoints to it so they can be added to an app via FastAPI.include_router or similar.
    """
    # _endpoints: List[EndpointDefinition] = []
    VERSION_API = '1.0'
    NAME_MODULE = ''

    BASE_TEMPLATE_PATH = '/{module}/{controller}/v{version}/{user_path}'
