from DB.Base import Base
from sqlmodel import Field


class Teacher(Base, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)

    def __repr__(self) -> str:
        return f"Teacher(id={self.id!r}, name={self.name!r})"
