import uuid
from typing import List, Generic, TypeVar  # 0. Import

import sqlalchemy
import uvicorn
from class_based_fastapi import Routable, get, put, post, delete
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlmodel import Session, create_engine

from database import run_async_upgrade
from models.models import Category, CategoryPUT, Book, BookPUT

app = FastAPI(debug=True)

engine = create_engine('postgresql://postgres:123456@localhost:5432/fastapi_example', echo=True)


@app.on_event("startup")
def on_startup():
    print("Start migration")
    run_async_upgrade()
    print("DB success upgrade !")


def get_session() -> Session:
    with Session(engine) as conn:
        yield conn


T = TypeVar('T')  # 1. Create generic type
TPut = TypeVar('TPut')  # 1. Create generic type


class BaseAPI(Routable, Generic[T, TPut]):  # 2. Create generic base API controller
    conn: Session = Depends(get_session)

    def __init__(self):
        self._type_db_model = self._get_type_generic(T)

    def _get_type_generic(self, tvar: TypeVar):
        return next(filter(lambda x: x['name'] == tvar.__name__, self.__class__.__generic_attribute__))['type']

    @get("")
    def get_list_categories(self) -> List[T]:  # 3. Specifying  generic types
        items = self.conn.execute(select(self._type_db_model)).scalars().all()
        return items

    @post("")
    def add_category(self, model: T) -> T:
        self.conn.add(model)
        self.conn.commit()
        return model

    @delete("{guid}")
    def delete_category(self, guid: str) -> bool:
        self.conn.execute(
            sqlalchemy.delete(self._type_db_model).filter(self._type_db_model.guid == uuid.UUID(guid))
        )
        self.conn.commit()
        return True

    @put("{guid}")
    def update_category(self, guid: str, model: TPut) -> T:  # 3. Specifying  generic types
        model_db = self.conn.execute(
            select(self._type_db_model).filter(self._type_db_model.guid == uuid.UUID(guid))
        ).scalar()
        # Update fields
        for name, val in model.dict(exclude_unset=True).items():
            setattr(model_db, name, val)
        self.conn.commit()
        self.conn.refresh(model_db)
        return model_db


# Categories
class CategoryAPI(BaseAPI[Category, CategoryPUT]):  # 4. Inheriting the base controller
    NAME_MODULE = Category.__name__


# Books
class BookAPI(BaseAPI[Book, BookPUT]):  # 4. Inheriting the base controller
    NAME_MODULE = Book.__name__


app.include_router(CategoryAPI.routes())  # 5. Include routes
app.include_router(BookAPI.routes())  # 5. Include routes
#
# if __name__ == "__main__":
#     uvicorn.run('runs:app', host="localhost", port=8001, reload=True, debug=True)
