import uuid
from typing import List

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy import select, delete
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


# region Categories
@app.get("/references/category")
def get_list_categories(conn: Session = Depends(get_session)) -> List[Category]:
    items = conn.execute(select(Category)).scalars().all()
    return items


@app.post("/references/category")
def add_category(model: Category, conn: Session = Depends(get_session)) -> Category:
    conn.add(model)
    conn.commit()
    return model


@app.delete("/references/category/{guid}")
def delete_category(guid: str, conn: Session = Depends(get_session)) -> bool:
    conn.execute(
        delete(Category).filter(Category.guid == uuid.UUID(guid))
    )
    conn.commit()
    return True


@app.put("/references/category/{guid}")
def update_category(guid: str, model: CategoryPUT, conn: Session = Depends(get_session)) -> Category:
    model_db = conn.execute(
        select(Category).filter(Category.guid == uuid.UUID(guid))
    ).scalar()
    # Update fields
    for name, val in model.dict(exclude_unset=True).items():
        setattr(model_db, name, val)
    conn.commit()
    conn.refresh(model_db)
    return model_db


# endregion

# region Books
@app.get("/references/books")
def get_list_books(conn: Session = Depends(get_session)) -> List[Book]:
    items = conn.execute(select(Book)).scalars().all()
    return items


@app.post("/references/books")
def add_book(model: Book, conn: Session = Depends(get_session)) -> Book:
    conn.add(model)
    conn.commit()
    return model


@app.delete("/references/books/{guid}")
def delete_book(guid: str, conn: Session = Depends(get_session)) -> bool:
    conn.execute(
        delete(Book).filter(Book.guid == uuid.UUID(guid))
    )
    conn.commit()
    return True


@app.put("/references/book/{guid}")
def update_book(guid: str, model: BookPUT, conn: Session = Depends(get_session)) -> Book:
    model_db = conn.execute(
        select(Book).filter(Book.guid == uuid.UUID(guid))
    ).scalar()
    # Update fields
    for name, val in model.dict(exclude_unset=True).items():
        setattr(model_db, name, val)
    conn.commit()
    conn.refresh(model_db)
    return model_db


# endregion
if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8001, reload=True, debug=True)
