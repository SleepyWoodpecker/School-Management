from DB.Base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, DateTime, FLOAT
from sqlalchemy.schema import PrimaryKeyConstraint
from datetime import datetime


class CourseRecord(Base):
    __tablename__ = "course_record"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("student.id"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teacher.id"), nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    grade: Mapped[float] = mapped_column(FLOAT)
    gpa: Mapped[float] = mapped_column(FLOAT)

    def __repr__(self) -> str:
        return f"CourseRecord(student_id={self.student_id!r}, teacher_id={self.teacher_id}, start_date={self.start_date}, grade={self.grade}, gpa={self.gpa})"
