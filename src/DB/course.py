from DB.Base import Base
from sqlmodel import Field, PrimaryKeyConstraint
from typing import Optional
from datetime import datetime


class Course_Record(Base, table=True):
    __table_args__ = (PrimaryKeyConstraint("student_id", "end_date"),)

    student_id: int = Field(foreign_key="student.id")
    end_date: datetime = Field(nullable=False)
    grade: Optional[float] = Field(default=None)

    def __repr__(self) -> str:
        return f"CourseRecord(student_id={self.student_id!r}, end_date={self.end_date!r}, grade={self.grade!r})"
