from DB.Base import Base
from sqlmodel import SQLModel


def init_db() -> None:
    SQLModel.metadata = Base.metadata
    SQLModel.metadata.create_all(bind=Base.engine, checkfirst=True)
