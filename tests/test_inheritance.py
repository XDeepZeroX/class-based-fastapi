from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.controllers import ExampleRoutableChildren, ExampleRoutableParent
from tests.utilities import check_api_methods, create_app


def test_override_array_method() -> None:
    client = create_app()

    response = client.get('/children/example-routable-children/v1.0/array')
    assert response.status_code == 200
    assert response.json() == [1, 2, 3]

    response = client.get('/parent/example-routable-parent/v1.1/array')
    assert response.status_code == 200
    assert response.json() == [1, 2, 3, 4]