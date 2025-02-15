from DB.Base import Base
from sqlmodel import Field, select, update
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, IntegrityError
from DB.course import Course_Record
from DB.teacher import Teacher
from DB.db_exceptions import DBAPIError, DBRecordNotFoundError

from models import StudentDataResponse, ChangeTeacherResponse


class Student(Base, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    teacher_id: int = Field(foreign_key="teacher.id")

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r}, teacher_id={self.teacher_id!r})"


class StudentDB:
    def get_all_cumulative_gpa_and_teacher_name(self) -> StudentDataResponse:
        """
        For each student in the DB, get their:
          (a) name
          (b) cumulative GPA up till this point in time
          (c) teacher name

        Args:
            None

        Returns:
            A list of StudentDataResponses

        Raises:
            DBAPIError: If there was an issue with the DB request
        """
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
            try:
                scores = session.exec(query)
                return [score._mapping for score in scores]

            except SQLAlchemyError as e:
                raise DBAPIError(
                    sql_statement=str(query.compile(dialect=postgresql.dialect())),
                    original_error=str(e),
                )

    def change_teacher(self, student_id: int, teacher_id: int) -> ChangeTeacherResponse:
        """
        Change the teacher assigned to the student

        Args:
            student_id: DB ID of student
            teacher_id: DB ID of teacher

        Returns:
            ChangeTeacherResponse

        Raises:
            DBRecordNotFoundError: requested resource does not exist on the DB
            DBAPIError: if there was any other issue with the DB request
        """
        with Base.session_scope() as session:
            update_student_query = (
                update(Student)
                .where(Student.id == student_id)
                .values(teacher_id=teacher_id)
            )

            update_student_query_sql = update_student_query.compile(
                dialect=postgresql.dialect()
            )

            try:

                update_result = session.exec(update_student_query)
                session.commit()

                # raise an error if the requested student cannot be found
                if update_result.rowcount == 0:
                    raise DBRecordNotFoundError(
                        message="The requested student cannot be found",
                        sql_statement=str(update_student_query_sql),
                        params=update_student_query_sql.params,
                    )

            except IntegrityError as e:
                raise DBRecordNotFoundError(
                    message="The requested teacher ID cannot be found in the DB",
                    sql_statement=update_student_query_sql,
                    params=update_student_query_sql.params,
                    original_error=str(e),
                )

            except SQLAlchemyError as e:
                raise DBRecordNotFoundError(
                    message="An exception occured when trying to update the student's teacher",
                    sql_statement=update_student_query_sql,
                    params=update_student_query_sql.params,
                    original_error=str(e),
                )

            find_updated_student_query = (
                select(
                    Student.name.label("student_name"),
                    Student.id.label("student_id"),
                    Teacher.name.label("updated_teacher_name"),
                    Teacher.id.label("updated_teacher_id"),
                )
                .where(Student.id == student_id)
                .join(Teacher, Teacher.id == Student.teacher_id)
            )

            find_updated_student_query_sql = find_updated_student_query.compile(
                dialect=postgresql.dialect()
            )

            try:
                updated_student = session.exec(find_updated_student_query).one()
                return updated_student._mapping

            except NoResultFound as e:
                raise DBRecordNotFoundError(
                    message="The requested student cannot be found after the update",
                    sql_statement=str(find_updated_student_query_sql),
                    params=find_updated_student_query_sql.params,
                    original_error=str(e),
                )

            except SQLAlchemyError as e:
                raise DBAPIError(
                    message="Exception occured when searching for student after the update to teacher id",
                    sql_statement=str(find_updated_student_query_sql),
                    params=find_updated_student_query_sql.params,
                    original_error=str(e),
                )
