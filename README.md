<p align="center">
    <em>Class based routing for FastAPI</em>
</p>
<p align="center">
<img src="https://img.shields.io/github/last-commit/XDeepZeroX/class-based-fastapi.svg">
<br />
<a href="https://pypi.org/project/class-based-fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/v/class-based-fastapi?label=class-based-fastapi" alt="Package version">
</a>
    <img src="https://img.shields.io/badge/python-3.6%20--%203.10-blue">
    <img src="https://img.shields.io/github/license/XDeepZeroX/class-based-fastapi">
</p>

---

**Documentation**:
<a href="https://XDeepZeroX.github.io/class-based-fastapi" target="_blank">https://XDeepZeroX.github.io/class-based-fastapi</a>

**Source Code**:
<a href="https://github.com/XDeepZeroX/class-based-fastapi" target="_blank">https://github.com/XDeepZeroX/class-based-fastapi</a>

---

<a href="https://fastapi.tiangolo.com">FastAPI</a> is a modern, fast web framework for building APIs with Python 3.6+.

---

## Features

Write Fast API Controllers (Classes) that can inherit route information from it's parent.

- This also allows to create a path prefix from a template and add api version information in the template.
- You don't need to duplicate the code, you can inherit it.
- To generate OpenAPI documentation, you do not need to explicitly specify the type of the return value, use Generics !

> Do the same with API methods as before, only more convenient.

See the [docs](https://XDeepZeroX.github.io/class-based-fastapi) for more details and examples.

## Requirements

This package is intended for use with any recent version of FastAPI (depending on `pydantic>=1.8.2`), and Python 3.6+.

## Installation

```sh
pip install class-based-fastapi
```

## Example


```python
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

if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8001, reload=True, debug=True)

```

![Class base API OpenAPI Docs](https://github.com/XDeepZeroX/class-based-fastapi/raw/main/docs/img/generics/Class_based_API.png)

[Next steps >>>](https://XDeepZeroX.github.io/class-based-fastapi)

## License

This project is licensed under the terms of
the [MIT](https://github.com/XDeepZeroX/class-based-fastapi/blob/main/LICENSE) license.