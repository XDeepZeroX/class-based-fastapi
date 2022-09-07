from typing import Generic, TypeVar, List, Union, Type, Any, Dict

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlmodel import SQLModel

from class_based_fastapi.decorators import post, get
from class_based_fastapi.routable import Routable
from tests.utilities import check_api_methods

# region MODELS

TReq = TypeVar('TReq')
TRes = TypeVar('TRes')
TReq1 = TypeVar('TReq1')
TRes1 = TypeVar('TRes1')


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


# endregion
# region Controllers
# region Simple Types
class BaseView_TestGeneric(Routable, Generic[TReq, TRes]):
    _injected = 1

    @post(path='add')
    def add(self, x: TReq) -> TRes:
        return BaseResponse(param1=999, param2='test')

    @get(path='')
    def list(self) -> List[TRes]:
        return list()


class ExampleRoutableParent_TestGeneric(BaseView_TestGeneric[BaseRequestBody, BaseResponse]):
    NAME_MODULE = 'Test'


class BaseViewParent_TestGeneric(BaseView_TestGeneric[TReq1, TRes1], Generic[TReq1, TRes1]):
    pass


class ExampleRoutableParent1_TestGeneric(BaseViewParent_TestGeneric[CloneBaseRequestBody, CloneBaseResponse]):
    pass


# endregion
# region Generic Types

class TestClass(SQLModel):
    data: Any


TReqGen1 = TypeVar('TReqGen1')
TReqGen2 = TypeVar('TReqGen2')
TResGen1 = TypeVar('TResGen1')

TReqGen3 = TypeVar('TReqGen3')
TReqGen4 = TypeVar('TReqGen4')
TResGen3 = TypeVar('TResGen3')


class BV_Generic(Routable, Generic[TReqGen1, TReqGen2, TResGen1]):
    _injected = 1

    @post(path='convert')
    def add(self, x: TReqGen1) -> List[TResGen1]:
        return [TRes(data=i) for i in x]

    @post(path='test/{x}')
    def test(self, x: str) -> str:
        return [TRes(data=i) for i in x]

    @get(path='get-list/{x}')
    def get_list(self, x: TReqGen2) -> List[TResGen1]:
        if isinstance(x, str):
            x = int(x)
        return [TRes(data=i) for i in range(x)]


class BV_Middle_Generic1(BV_Generic[TReqGen3, TReqGen4, TResGen3], Generic[TReqGen3, TReqGen4, TResGen3]):
    pass


class BVParent_Generic2(BV_Middle_Generic1[List[int], int, Dict[str, TestClass]]):
    pass


class BVParent_Generic3(BV_Middle_Generic1[List[int], str, TestClass]):
    pass


# endregion
# endregion

###################################################
#################### TESTS ########################
###################################################
class TrueRoute(SQLModel):
    RequestType: Union[type, Any, None]
    ResponseType: Union[type, Any, None]


def create_app(controllers: List[Type[Routable]]) -> FastAPI:
    app = FastAPI()
    for controller in controllers:
        app.include_router(controller.routes())
    check_api_methods(app)
    return app


ORIGIN = '__origin__'
ARGS = '__args__'


def is_equal_types(real_val, true_val) -> bool:
    if hasattr(real_val, ORIGIN) and hasattr(true_val, ORIGIN):
        return getattr(real_val, ORIGIN) == getattr(true_val, ORIGIN) \
               and getattr(real_val, ARGS) == getattr(true_val, ARGS)

    return real_val is true_val \
           or (real_val is None and true_val is None) \
           or (true_val is str and real_val is None) \
           or isinstance(real_val, true_val)


def test_generic__generic_types() -> None:
    app = create_app(
        [
            BVParent_Generic2,
            BVParent_Generic3,
        ]
    )
    true_route = {
        '/bv-parent-generic2/v1.0/convert': TrueRoute(RequestType=List[int], ResponseType=List[Dict[str, TestClass]]),
        '/bv-parent-generic3/v1.0/get-list/{x}': TrueRoute(RequestType=str, ResponseType=List[TestClass]),
        '/bv-parent-generic3/v1.0/test/{x}': TrueRoute(RequestType=str, ResponseType=str),
    }
    for path, type_ in true_route.items():
        app_routes: List[APIRoute] = list(filter(lambda x: x.path == path, app.routes))
        assert len(app_routes) == 1

        response_model = app_routes[0].response_model
        assert is_equal_types(response_model, type_.ResponseType)

        request_type = None if app_routes[0].body_field is None else app_routes[0].body_field.annotation
        assert is_equal_types(request_type, type_.RequestType)


def test_generic() -> None:
    app = create_app(
        [
            BaseView_TestGeneric,
            ExampleRoutableParent_TestGeneric,
            ExampleRoutableParent1_TestGeneric,
        ]
    )

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

        request_type = None if app_routes[0].body_field is None else app_routes[0].body_field.annotation
        assert is_equal_types(request_type, type_.RequestType)


if __name__ == '__main__':
    # test_generic__generic_types()

    create = lambda: create_app(
        [
            # BVParent_Generic1,
            BVParent_Generic2
        ]
    )
    uvicorn.run(create, host="localhost", port=9090)
