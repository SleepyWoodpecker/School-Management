from DB.Base import Base
from sqlmodel import Field


class Student(Base, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r})"
