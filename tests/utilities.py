from fastapi import FastAPI
from starlette.testclient import TestClient

from tests.controllers import ExampleRoutableChildren, ExampleRoutableParent


def check_api_methods(app: FastAPI):
    methods = '\n'.join(map(lambda x: f'[{x.methods}]: {x.path}', app.routes))
    print(
        f'''
Список методов
----------------
{methods}
----------------
    '''
    )


def create_app() -> TestClient:
    app = FastAPI()
    app.include_router(ExampleRoutableChildren.routes())
    app.include_router(ExampleRoutableParent.routes())

    check_api_methods(app)

    return TestClient(app)
