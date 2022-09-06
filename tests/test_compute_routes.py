from typing import List, Any, Union

from fastapi import Depends
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute, APIRouter

from class_based_fastapi import Routable, get, post, put, delete, patch


def response_(n: int) -> str:
    return f'Ok {n}'


NAME_MODULE_CHILDREN = 'Children'
REST_NAME_MODULE_CHILDREN = 'children'
NAME_MODULE_PARENT = 'Parent'
REST_NAME_MODULE_PARENT = 'parent'


def get_db():
    return 99


class ExampleRoutableChildren_RoutesTest(Routable):
    NAME_MODULE = NAME_MODULE_CHILDREN
    db: int = Depends(get_db)
    _injected = 1

    def __init__(self, db_=Depends(get_db)) -> None:
        self.db_from_init = db_

    @get(path='{id}', response_class=PlainTextResponse)
    def get_(self, id: int) -> str:
        return response_(self._injected)

    @post(path='', response_class=PlainTextResponse)
    def add(self) -> str:
        return response_(self._injected)

    @put(path='', response_class=PlainTextResponse)
    async def put(self) -> str:
        return response_(self._injected)

    @delete(path='{id}', response_class=PlainTextResponse)
    async def delete_(self, id: str) -> str:
        return response_(self._injected)

    @patch(path='{id}', response_class=PlainTextResponse)
    async def patch(self, id: str) -> str:
        return response_(self._injected)


class ExampleRoutableParent_RoutesTest(ExampleRoutableChildren_RoutesTest):
    NAME_MODULE = NAME_MODULE_PARENT
    VERSION_API = '1.1'
    _injected = 2


class TrueRoute:
    def __init__(
            self,
            path: str
    ):
        self.path = path

    def __repr__(self):
        return f'<path={self.path}>'


def get_methods_by_method(routes: List[APIRoute], method: str) -> List[APIRoute]:
    """Получение списка маршрутов API

    Args:
        routes: Список всех маршрутов
        method: Метод API (GET / POST / PUT / DELETE / PATCH / ...)

    Returns: Список подходящих маршрутов
    """
    return list(filter(lambda x: str.upper(method) in x.methods, routes))


def check_route(routes: Union[APIRouter, List[APIRoute]], true_result: dict[str, Any]) -> None:
    if isinstance(routes, APIRouter):
        routes = routes.routes

    for method, true_result in true_result.items():
        routes_by_method = get_methods_by_method(routes, method)

        assert len(routes_by_method) == len(true_result)

        paths_routes = list(map(lambda x: x.path, routes_by_method))
        paths_routes.sort()

        true_paths = list(map(lambda x: x.path, true_result))
        true_paths.sort()

        for i in range(len(true_result)):
            assert paths_routes[i] == true_paths[i]


def test_compute_path_parent():
    result = {
        'GET': [
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1/{id}')
        ],
        'POST': [
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1')
        ],
        'PUT': [
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1')
        ],
        'DELETE': [
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1/{id}')
        ],
        'PATCH': [
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1/{id}')
        ]
    }
    check_route(
        ExampleRoutableParent_RoutesTest.routes(),
        result
    )


def test_compute_path_children():
    result = {
        'GET': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0/{id}')
        ],
        'POST': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0')
        ],
        'PUT': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0')
        ],
        'DELETE': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0/{id}')
        ],
        'PATCH': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0/{id}')
        ]
    }
    check_route(
        ExampleRoutableChildren_RoutesTest.routes(),
        result
    )


def test_more_routes() -> None:
    app = FastAPI()
    app.include_router(ExampleRoutableParent_RoutesTest.routes())
    app.include_router(ExampleRoutableChildren_RoutesTest.routes())

    routes = list(filter(lambda x: isinstance(x, APIRoute), app.routes))

    result = {
        'GET': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0/{id}'),
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1/{id}')
        ],
        'POST': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0'),
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1')
        ],
        'PUT': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0'),
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1')
        ],
        'DELETE': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0/{id}'),
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1/{id}')
        ],
        'PATCH': [
            TrueRoute(path='/children/example-routable-children-routes-test/v1.0/{id}'),
            TrueRoute(path='/parent/example-routable-parent-routes-test/v1.1/{id}')
        ]
    }

    check_route(
        routes,
        result
    )
