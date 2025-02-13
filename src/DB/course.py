from DB.Base import Base
from sqlmodel import Field, PrimaryKeyConstraint
from typing import Optional
from datetime import datetime


class Course_Record(Base, table=True):
    __table_args__ = (PrimaryKeyConstraint("student_id", "start_date"),)

    student_id: int = Field(foreign_key="student.id")
    start_date: datetime = Field(nullable=False)
    grade: Optional[float] = Field(default=None)
    gpa: Optional[float] = Field(default=None)

    def __repr__(self) -> str:
        return f"CourseRecord(student_id={self.student_id!r}, teacher_id={self.teacher_id}, start_date={self.start_date}, grade={self.grade}, gpa={self.gpa})"
