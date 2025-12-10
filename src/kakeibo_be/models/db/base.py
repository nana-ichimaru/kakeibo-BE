from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from kakeibo_be.core.database import get_database_url

database_url = get_database_url()
engine = create_engine(database_url, echo=False)

Base = declarative_base()

session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session]:
    db = session()
    try:
        yield db
    finally:
        db.close()
