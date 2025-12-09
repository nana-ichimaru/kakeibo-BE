from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from kakeibo_be.core.database import get_database_url

database_url = get_database_url()
engine = create_engine(database_url, echo=False)

Base = declarative_base()