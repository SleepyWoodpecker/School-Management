from DB.Base import Base
from sqlmodel import Field, select
from sqlalchemy import func
from DB.course import Course_Record
from DB.teacher import Teacher


class Student(Base, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    teacher_id: int = Field(foreign_key="teacher.id")

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r}, teacher_id={self.teacher_id!r})"


class StudentDB:
    def get_all_cumulative_gpa_and_teacher_name(self):
        subquery = (
            select(
                Student.name.label("student_name"),
                Student.teacher_id.label("student_teacher_id"),
                func.avg(Course_Record.gpa).label("cumulative_gpa"),
            )
            .join(Student, Student.id == Course_Record.student_id)
            .group_by(Student.id)
        ).subquery()
        query = select(
            subquery.c.student_name,
            subquery.c.cumulative_gpa,
            Teacher.name.label("teacher_name"),
        ).join(Teacher, subquery.c.student_teacher_id == Teacher.id)

        with Base.session_scope() as session:
            scores = session.exec(query)
            return [score._mapping for score in scores]
