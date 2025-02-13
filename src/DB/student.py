from DB.Base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR


class Student(Base):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR)

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r})"
