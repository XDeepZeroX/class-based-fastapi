from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine
from alembic import command
from alembic.config import Config

engine = create_engine('postgresql://postgres:672412Aa@localhost:5432/fastapi_example', echo=True, future=True)

alembic_cfg = Config('alembic.ini')
alembic_cfg.set_main_option('script_location', 'alembic')


def run_upgrade(connection, cfg):
    """Запуск команды миграции."""
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


def run_async_upgrade():
    """Подготовка к запуску команды миграции"""
    with engine.begin() as conn:
        run_upgrade(conn, alembic_cfg)


def get_session() -> Session:
    """Получение сессии."""
    async_session = sessionmaker(
        engine, class_=Session, expire_on_commit=False
    )
    with async_session() as session:
        yield session
