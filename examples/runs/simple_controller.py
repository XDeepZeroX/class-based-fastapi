import uuid
from typing import List

import sqlalchemy
import uvicorn
from class_based_fastapi import Routable, get, put, post, delete  # 0. Import
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlmodel import Session, create_engine

from database import run_async_upgrade
from models.models import Category, CategoryPUT, Book, BookPUT

app = FastAPI(debug=True)

engine = create_engine('postgresql://postgres:672412Aa@localhost:5432/fastapi_example', echo=True)


@app.on_event("startup")
def on_startup():
    print("Start migration")
    run_async_upgrade()
    print("DB success upgrade !")


def get_session() -> Session:
    with Session(engine) as conn:
        yield conn


# region Categories
class CategoryAPI(Routable):  # 1. Create class
    NAME_MODULE = Category.__name__
    conn: Session = Depends(get_session)  # 2. Add depend

    @get("")
    def get_list_categories(self) -> List[Category]:  # 3. Add `self` param and remove conn
        items = self.conn.execute(select(Category)).scalars().all()
        return items

    @post("")
    def add_category(self, model: Category) -> Category:  # 3. Add `self` param and remove conn
        self.conn.add(model)
        self.conn.commit()
        return model

    @delete("{guid}")
    def delete_category(self, guid: str) -> bool:  # 3. Add `self` param and remove conn
        self.conn.execute(
            sqlalchemy.delete(Category).filter(Category.guid == uuid.UUID(guid))
        )
        self.conn.commit()
        return True

    @put("{guid}")
    def update_category(self, guid: str, model: CategoryPUT) -> Category:  # 3. Add `self` param and remove conn
        model_db = self.conn.execute(
            select(Category).filter(Category.guid == uuid.UUID(guid))
        ).scalar()
        # Update fields
        for name, val in model.dict(exclude_unset=True).items():
            setattr(model_db, name, val)
        self.conn.commit()
        self.conn.refresh(model_db)
        return model_db


# endregion

# region Books

class BookAPI(Routable):  # 1. Create class
    NAME_MODULE = Book.__name__
    conn: Session = Depends(get_session)  # 2. Add depend

    @get("")
    def get_list_books(self, conn: Session = Depends(get_session)) -> List[Book]:  # 3. Add `self` param and remove conn
        items = conn.execute(select(Book)).scalars().all()
        return items

    @post("")
    def add_book(self, model: Book,
                 conn: Session = Depends(get_session)) -> Book:  # 3. Add `self` param and remove conn
        conn.add(model)
        conn.commit()
        return model

    @delete("{guid}")
    def delete_book(self, guid: str) -> bool:  # 3. Add `self` param and remove conn
        self.conn.execute(
            delete(Book).filter(Book.guid == uuid.UUID(guid))
        )
        self.conn.commit()
        return True

    @put("{guid}")
    def update_book(self, guid: str, model: BookPUT) -> Book:  # 3. Add `self` param and remove conn
        model_db = self.conn.execute(
            select(Book).filter(Book.guid == uuid.UUID(guid))
        ).scalar()
        # Update fields
        for name, val in model.dict(exclude_unset=True).items():
            setattr(model_db, name, val)
        self.conn.commit()
        self.conn.refresh(model_db)
        return model_db


app.include_router(CategoryAPI.routes())  # 4. Include routes
app.include_router(BookAPI.routes())  # 4. Include routes

# endregion
# if __name__ == "__main__":
#     uvicorn.run('main:app', host="localhost", port=8001, reload=True, debug=True)
