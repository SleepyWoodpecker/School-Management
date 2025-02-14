from DB.Base import Base
from sqlmodel import SQLModel

from sqlalchemy.exc import OperationalError
from DB.db_exceptions import DBConnectionError


def init_db() -> None:
    try:
        SQLModel.metadata = Base.metadata
        SQLModel.metadata.create_all(bind=Base.engine, checkfirst=True)
    except OperationalError as e:
        raise DBConnectionError("Could not connect to the DB")
