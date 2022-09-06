from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.controllers import ExampleRoutableChildren, ExampleRoutableParent
from tests.utilities import check_api_methods, create_app


def test_inheritance_routes_children() -> None:
    client = create_app()

    response = client.get('/children/example-routable-children/v1.0/attr-depends')
    assert response.status_code == 200
    assert response.text == '99'

    response = client.get('/parent/example-routable-parent/v1.1/attr-depends')
    assert response.status_code == 200
    assert response.text == '99'

def test_init_depends() -> None:
    client = create_app()

    response = client.get('/children/example-routable-children/v1.0/init-depends')
    assert response.status_code == 200
    assert response.text == '99'

    response = client.get('/parent/example-routable-parent/v1.1/init-depends')
    assert response.status_code == 200
    assert response.text == '99'


def test_method_depends() -> None:
    client = create_app()

    response = client.get('/parent/example-routable-parent/v1.1/method-depends')
    assert response.status_code == 200
    assert response.text == '99'

    response = client.get('/children/example-routable-children/v1.0/method-depends')
    assert response.status_code == 200
    assert response.text == '99'
