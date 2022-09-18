from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.controllers import ExampleRoutableChildren, ExampleRoutableParent, REST_NAME_MODULE_CHILDREN, \
    REST_NAME_MODULE_PARENT
from tests.utilities import check_api_methods


def response_(n: int) -> str:
    return f'Ok {n}'


class Base:
    param1: str
    param2: str


def requests_(client, status: int, module: str, controller: str, version: str = '1.0', response_: str = None):

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
    n = 1
    app.include_router(ExampleRoutableChildren.routes())

    check_api_methods(app)

    client = TestClient(app)

    resp = response_(n)

    # Children
    requests_(client, 200, REST_NAME_MODULE_CHILDREN, 'example-routable-children', response_=resp)

    ## Parent

    requests_(client, 404, REST_NAME_MODULE_PARENT, 'example-routable-parent', version='1.1')


def test_inheritance_routes_parent() -> None:
    app = FastAPI()
    n = 2
    t = ExampleRoutableParent
    app.include_router(t.routes())

    client = TestClient(app)

    resp = response_(n)

    # Children
    requests_(client, 404, REST_NAME_MODULE_CHILDREN, 'example-routable-children')

    ## Parent

    requests_(client, 200, REST_NAME_MODULE_PARENT, 'example-routable-parent', response_=resp, version='1.1')


def test_inheritance_routes() -> None:
    app = FastAPI()
    t1 = ExampleRoutableChildren
    t2 = ExampleRoutableParent
    app.include_router(t1.routes())
    app.include_router(t2.routes())

    client = TestClient(app)

    # Children
    requests_(client, 200, REST_NAME_MODULE_CHILDREN, 'example-routable-children', response_=response_(1))

    ## Parent

    requests_(client, 200, REST_NAME_MODULE_PARENT, 'example-routable-parent', response_=response_(2), version='1.1')


def main():
    app = FastAPI()
    t1 = ExampleRoutableChildren
    t2 = ExampleRoutableParent
    app.include_router(t1.routes())
    app.include_router(t2.routes())

    check_api_methods(app)


if "__main__" == __name__:
    # main()
    test_inheritance_routes_children()
