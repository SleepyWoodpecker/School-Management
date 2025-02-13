from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv, find_dotenv
from contextlib import contextmanager
import os

load_dotenv(find_dotenv())


class Base(DeclarativeBase):
    """Base factory class to create basic CRUD functions"""

    engine = create_engine(os.getenv("NEON_DB_CONNECTION_URL"))
    Session = sessionmaker(bind=engine)

    @classmethod
    @contextmanager
    def session_scope(cls):
        """context manager to facilitate SQLAlchemy transactions"""
        session = cls.Session()
        yield session
