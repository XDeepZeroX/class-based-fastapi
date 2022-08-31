from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from class_based_fastapi import Routable, get, post, put, delete, patch


def response_(n: int) -> str:
    return f'Ok {n}'


_NAME_MODULE = 'TestView'
_REST_NAME_MODULE = 'test-view'


class ExampleRoutableChildren(Routable):
    NAME_MODULE = _NAME_MODULE

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
    pass


def requests(client, status: int, controller: str, response_: str = None):

    response = client.get(f'{_REST_NAME_MODULE}/{controller}/v1.0/100')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.delete(f'{_REST_NAME_MODULE}/{controller}/v1.0/100')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.post(f'{_REST_NAME_MODULE}/{controller}/v1.0')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.put(f'{_REST_NAME_MODULE}/{controller}/v1.0')
    assert response.status_code == status
    if response_ is not None:
        assert response.text == response_

    response = client.patch(f'{_REST_NAME_MODULE}/{controller}/v1.0/100')
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
    requests(client, 200, 'example-routable-children', resp)

    ## Parent

    requests(client, 404, 'example-routable-parent')


def test_inheritance_routes_parent() -> None:
    app = FastAPI()
    n = 2
    t = ExampleRoutableParent(n)
    app.include_router(t.router)

    client = TestClient(app)

    resp = response_(n)

    # Children
    requests(client, 404, 'example-routable-children')

    ## Parent

    requests(client, 200, 'example-routable-parent', resp)


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
    requests(client, 200, 'example-routable-children', resp)

    ## Parent

    requests(client, 200, 'example-routable-parent', resp)
