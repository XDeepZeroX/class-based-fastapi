from typing import List, Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from class_based_fastapi.decorators import get
from class_based_fastapi.routable import Routable
from tests.utilities import check_api_methods


# region MODELS
# region Default
class CTagging_Default(Routable):
    _injected = 1

    @get(path='add')
    def add(self) -> int:
        return 123


class CTagging_Default2(CTagging_Default):
    NAME_MODULE = 'Test'


# endregion
# region ByAttrClass
class CTagging_ByAttrClass1(Routable):
    _injected = 1

    @get(path='add')
    def add(self) -> int:
        return 123


class CTagging_ByAttrClass2(CTagging_ByAttrClass1):
    TAGS = ['tag2']


class CTagging_ByAttrClass3(CTagging_ByAttrClass2):
    TAGS = ['tag3']


# endregion
# region ByAttrClassAndDecorator
class CTagging_ByAttrAndDec1(Routable):
    _injected = 1

    @get(path='add')
    def add(self) -> int:
        return 123


class CTagging_ByAttrAndDec2(CTagging_ByAttrAndDec1):
    TAGS = ['tag2']

    @get(path='', tags=['get_tag'])
    def get_(self) -> str:
        return 'ok'


class CTagging_ByAttrAndDec3(CTagging_ByAttrAndDec2):
    TAGS = ['tag3']


# endregion
# endregion

class TrueTags(SQLModel):
    tags: Optional[List[str]]
    path: List[str]


def test_routes_respond() -> None:
    app = FastAPI()
    app.include_router(CTagging_Default.routes())
    app.include_router(CTagging_Default2.routes())
    app.include_router(CTagging_ByAttrClass1.routes())
    app.include_router(CTagging_ByAttrClass2.routes())
    app.include_router(CTagging_ByAttrClass3.routes())
    app.include_router(CTagging_ByAttrAndDec1.routes())
    app.include_router(CTagging_ByAttrAndDec2.routes())
    app.include_router(CTagging_ByAttrAndDec3.routes())

    check_api_methods(app)

    client = TestClient(app)

    tests = [
        TrueTags(path=['/c-tagging-default/v1.0/add'], tags=[CTagging_Default.__name__]),
        TrueTags(path=['/test/c-tagging-default2/v1.0/add'], tags=[CTagging_Default2.__name__]),
        TrueTags(path=['/c-tagging-by-attr-class1/v1.0/add'], tags=[CTagging_ByAttrClass1.__name__]),
        TrueTags(path=['/c-tagging-by-attr-class2/v1.0/add'], tags=['tag2']),
        TrueTags(path=['/c-tagging-by-attr-class3/v1.0/add'], tags=['tag3']),
        TrueTags(path=['/c-tagging-by-attr-and-dec1/v1.0/add'], tags=[CTagging_ByAttrAndDec1.__name__]),
        TrueTags(path=['/c-tagging-by-attr-and-dec2/v1.0/add'], tags=['tag2']),
        TrueTags(path=['/c-tagging-by-attr-and-dec3/v1.0/add'], tags=['tag3']),
        TrueTags(
            path=['/c-tagging-by-attr-and-dec2/v1.0', '/c-tagging-by-attr-and-dec3/v1.0'],
            tags=['get_tag']
        ),
    ]

    routes = app.routes
    for test in tests:
        for path in test.path:
            route = list(filter(lambda x: x.path == path, routes))[0]

            assert route.tags == test.tags
