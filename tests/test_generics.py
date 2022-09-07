from typing import Generic, TypeVar, List, Union

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import SQLModel

from class_based_fastapi.decorators import post
from class_based_fastapi.routable import Routable
from tests.utilities import check_api_methods

# region MODELS

TReq = TypeVar('TReq')
TRes = TypeVar('TRes')


class BaseRequestBody(SQLModel):
    param1: int
    param2: str


class CloneBaseRequestBody(BaseRequestBody):
    param3: float
    param4: float


class BaseResponse(SQLModel):
    param1: int
    param2: str


class CloneBaseResponse(BaseResponse):
    param3: float


class BaseView_TestGeneric(Routable, Generic[TReq, TRes]):
    _injected = 1

    @post(path='add')
    def add(self, x: TReq) -> TRes:
        return BaseResponse(param1=999, param2='test')


class ExampleRoutableParent_TestGeneric(BaseView_TestGeneric[BaseRequestBody, BaseResponse]):
    NAME_MODULE = 'Test'


TReq1 = TypeVar('TReq1')
TRes1 = TypeVar('TRes1')


class BaseViewParent_TestGeneric(BaseView_TestGeneric[TReq1, TRes1], Generic[TReq1, TRes1]):
    pass


class ExampleRoutableParent1_TestGeneric(BaseViewParent_TestGeneric[CloneBaseRequestBody, CloneBaseResponse]):
    pass


# endregion

###################################################
#################### TESTS ########################
###################################################
class TrueRoute(SQLModel):
    RequestType: Union[type, None]
    ResponseType: Union[type, None]


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(BaseView_TestGeneric.routes())
    app.include_router(ExampleRoutableParent_TestGeneric.routes())
    app.include_router(ExampleRoutableParent1_TestGeneric.routes())
    check_api_methods(app)
    return app


def is_equal_types(one, two) -> bool:
    return one is two \
           or (one is None and two is None) \
           or isinstance(one, two)


def test_generic() -> None:
    app = create_app()

    true_route = {
        '/example-routable-parent1-test-generic/v1.0/add': TrueRoute(
            RequestType=CloneBaseRequestBody, ResponseType=CloneBaseResponse
        ),
        '/test/example-routable-parent-test-generic/v1.0/add': TrueRoute(
            RequestType=BaseRequestBody,
            ResponseType=BaseResponse,
        ),
        '/base-view-test-generic/v1.0/add': TrueRoute(ResponseType=TypeVar),
    }
    for path, type_ in true_route.items():
        app_routes: List[APIRoute] = list(filter(lambda x: x.path == path, app.routes))
        assert len(app_routes) == 1

        response_model = app_routes[0].response_model
        assert is_equal_types(response_model, type_.ResponseType)

        request_type = None if app_routes[0].body_field is None else app_routes[0].body_field.type_
        assert is_equal_types(request_type, type_.RequestType)
