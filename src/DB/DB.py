from DB.Base import Base


def init_db() -> None:
    Base.metadata.create_all(bind=Base.engine, checkfirst=True)
