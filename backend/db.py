import os
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel

_engine = None  # Internal variable to hold the engine

def get_engine():
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        _engine = create_engine(database_url, echo=True)
    return _engine

def create_db_and_tables():
    SQLModel.metadata.create_all(get_engine())

def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session