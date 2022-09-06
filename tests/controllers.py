from typing import List

from fastapi import Depends
from fastapi.responses import PlainTextResponse

from class_based_fastapi import Routable, get, post, put, delete, patch
from fastapi.responses import JSONResponse


def response_(n: int) -> str:
    return f'Ok {n}'


NAME_MODULE_CHILDREN = 'Children'
REST_NAME_MODULE_CHILDREN = 'children'
NAME_MODULE_PARENT = 'Parent'
REST_NAME_MODULE_PARENT = 'parent'


def get_db():
    return 99


class ExampleRoutableChildren(Routable):
    NAME_MODULE = NAME_MODULE_CHILDREN
    db: int = Depends(get_db)
    _injected = 1

    def __init__(self, db_=Depends(get_db)) -> None:
        self.db_from_init = db_

    @get(path='{id:int}', response_class=PlainTextResponse)
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

    @get(path='attr-depends', response_model=int)
    async def get_class_attr_depends(self) -> int:
        return self.db

    @get(path='init-depends', response_model=int)
    async def get_init_depends(self) -> int:
        return self.db_from_init

    @get(path='method-depends', response_model=int)
    async def get_method_depends(self, db: int = Depends(get_db)) -> int:
        return db

    @get(path='array', response_model=List[int], response_class=JSONResponse)
    async def get_array(self) -> List[int]:
        return [1, 2, 3]


class ExampleRoutableParent(ExampleRoutableChildren):
    NAME_MODULE = NAME_MODULE_PARENT
    VERSION_API = '1.1'
    _injected = 2

    async def get_array(self) -> List[int]:
        return [1, 2, 3, 4]
