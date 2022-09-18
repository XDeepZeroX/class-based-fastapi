from typing import List

from fastapi import FastAPI, Depends
from sqlmodel import Session, create_engine

from class_based_fastapi import Routable, get, put, post, delete  # 0. Import
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

# region Categories
class CategoryAPI(Routable):  # 1. Create class
    NAME_MODULE = Category.__name__
    conn: Session = Depends(get_session)  # 2. Add depend

    @get("")
    def get_list_categories(self) -> List[Category]:  # 3. Add `self` param and remove conn
        ...

    @post("")
    def add_category(self, model: Category) -> Category:  # 3. Add `self` param and remove conn
        ...

    @delete("{guid}")
    def delete_category(self, guid: str) -> bool:  # 3. Add `self` param and remove conn
        ...

    @put("{guid}")
    def update_category(self, guid: str, model: CategoryPUT) -> Category:  # 3. Add `self` param and remove conn
        ...
# endregion

# region Books
class BookAPI(Routable):  # 1. Create class
    NAME_MODULE = Book.__name__
    conn: Session = Depends(get_session)  # 2. Add depend

    @get("")
    def get_list_books(self, conn: Session = Depends(get_session)) -> List[Book]:  # 3. Add `self` param and remove conn
        ...

    @post("")
    def add_book(self, model: Book,
                 conn: Session = Depends(get_session)) -> Book:  # 3. Add `self` param and remove conn
        ...

    @delete("{guid}")
    def delete_book(self, guid: str) -> bool:  # 3. Add `self` param and remove conn
        ...

    @put("{guid}")
    def update_book(self, guid: str, model: BookPUT) -> Book:  # 3. Add `self` param and remove conn
        ...
# endregion

app.include_router(CategoryAPI.routes())  # 4. Include routes
app.include_router(BookAPI.routes())  # 4. Include routes