from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import Engine
from dotenv import load_dotenv, find_dotenv
from contextlib import contextmanager
import os
from typing import ClassVar

load_dotenv(find_dotenv())


class Base(SQLModel):
    """Base class to perform session management for DB trasanctions"""

    engine: ClassVar[Engine] = create_engine(
        os.getenv("NEON_DB_CONNECTION_URL"),
        echo=os.getenv("IS_DEV_MODE") == "True",
    )

    @classmethod
    @contextmanager
    def session_scope(cls):
        """context manager to facilitate SQL transactions"""
        session = Session(cls.engine)
        try:
            yield session

        finally:
            session.close()
