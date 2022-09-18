import uuid
from typing import Optional

from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field


class Base(SQLModel):
    guid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

    @declared_attr
    def __pk__(cls) -> str:
        """Первичный ключ таблицы."""
        return f'{cls.__tablename__}.{cls.guid.__dict__["key"]}'


class Category(Base, table=True):
    name: str


class CategoryPUT(SQLModel):
    name: Optional[str]


class Book(Base, table=True):
    name: str
    categoryId: Optional[uuid.UUID] = Field(foreign_key=Category.__pk__)


class BookPUT(SQLModel):
    name: Optional[str]
    categoryId: Optional[uuid.UUID]
