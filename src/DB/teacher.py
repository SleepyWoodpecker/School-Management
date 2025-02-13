from DB.Base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import VARCHAR


class Teacher(Base):
    __tablename__ = "teacher"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR)

    def __repr__(self) -> str:
        return f"Teacher(id={self.id!r}, name={self.name!r})"
