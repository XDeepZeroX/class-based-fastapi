from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from class_based_fastapi import Routable, get, post, put, delete, patch


def response_(n: int) -> str:
    return f'Ok {n}'


_NAME_MODULE_CHILDREN = 'TestView'
_REST_NAME_MODULE_CHILDREN = 'test-view'
_NAME_MODULE_PARENT = 'Parent'
_REST_NAME_MODULE_PARENT = 'parent'


class ExampleRoutableChildren(Routable):
    NAME_MODULE = _NAME_MODULE_CHILDREN

    def __init__(self, injected: int) -> None:
        super().__init__()
        self._injected = injected

    @get(path='{id}', response_class=PlainTextResponse)
    def get(self, id: int) -> str:
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


class ExampleRoutableParent(ExampleRoutableChildren):
    NAME_MODULE = _NAME_MODULE_PARENT
    VERSION_API = '1.1'


def requests(client, status: int, module: str, controller: str, version: str = '1.0', response_: str = None):

    response = client.get(f'{module}/{controller}/v{version}/100')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.delete(f'{module}/{controller}/v{version}/100')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.post(f'{module}/{controller}/v{version}')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.put(f'{module}/{controller}/v{version}')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.patch(f'{module}/{controller}/v{version}/100')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_


def test_inheritance_routes_children() -> None:
    app = FastAPI()
    n = 2
    t = ExampleRoutableChildren(n)
    app.include_router(t.router)

    client = TestClient(app)

    resp = response_(n)

    # Children
    requests(client, 200, _REST_NAME_MODULE_CHILDREN, 'example-routable-children', response_=resp)

    ## Parent

    requests(client, 404, _REST_NAME_MODULE_PARENT, 'example-routable-parent', version='1.1')


def test_inheritance_routes_parent() -> None:
    app = FastAPI()
    n = 2
    t = ExampleRoutableParent(n)
    app.include_router(t.router)

    client = TestClient(app)

    resp = response_(n)

    # Children
    requests(client, 404, _REST_NAME_MODULE_CHILDREN, 'example-routable-children')

    ## Parent

    requests(client, 200, _REST_NAME_MODULE_PARENT, 'example-routable-parent', response_=resp, version='1.1')


def test_inheritance_routes() -> None:
    app = FastAPI()
    n = 2
    t1 = ExampleRoutableChildren(n)
    t2 = ExampleRoutableParent(n)
    app.include_router(t1.router)
    app.include_router(t2.router)

    client = TestClient(app)

    resp = response_(n)

    # Children
    requests(client, 200, _REST_NAME_MODULE_CHILDREN, 'example-routable-children', response_=resp)

    ## Parent

    requests(client, 200, _REST_NAME_MODULE_PARENT, 'example-routable-parent', response_=resp, version='1.1')
