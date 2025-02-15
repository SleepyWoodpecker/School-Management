from DB.Base import Base
from sqlmodel import Field, select, update

# choice of type import: https://docs.sqlalchemy.org/en/20/core/type_basics.html
from sqlalchemy import func, FLOAT, and_
from sqlalchemy.sql import Values, column
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, IntegrityError
from DB.course import Course_Record
from DB.teacher import Teacher
from DB.db_exceptions import DBAPIError, DBRecordNotFoundError
from datetime import datetime

from models import StudentDataResponse, ChangeTeacherResponse
from data import gpa_mapping


class Student(Base, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    teacher_id: int = Field(foreign_key="teacher.id")

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r}, teacher_id={self.teacher_id!r})"


class StudentDB:
    def __init__(self):
        self.gpa_conversion_scale = Values(
            column("lower_bound", FLOAT),
            column("upper_bound", FLOAT),
            column("gpa", FLOAT),
            name="gpa_conversion",
        ).data(gpa_mapping)

    def get_all_cumulative_gpa_and_teacher_name(self) -> list[StudentDataResponse]:
        """
        For each student in the DB, get their:
          (a) name
          (b) cumulative GPA up till this point in time
          (c) teacher name

        Args:
            None

        Returns:
            A list of `StudentDataResponses`

        Raises:
            `DBAPIError`: If there was an issue with the DB request
        """
        # put a GPA conversion table here
        # can implement some function to change it in the future to support curving

        score_to_gpa_query = (
            select(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                self.gpa_conversion_scale.c.gpa.label("gpa"),
                Course_Record.grade.label("grade"),
                Student.teacher_id.label("student_teacher_id"),
            )
            .join(Student, Student.id == Course_Record.student_id)
            .join(
                self.gpa_conversion_scale,
                and_(
                    Course_Record.grade >= self.gpa_conversion_scale.c.lower_bound,
                    Course_Record.grade <= self.gpa_conversion_scale.c.upper_bound,
                ),
            )
        )

        query = (
            select(
                score_to_gpa_query.c.student_name.label("student_name"),
                Teacher.name.label("teacher_name"),
                func.avg(score_to_gpa_query.c.gpa).label("cumulative_gpa"),
            )
            .join(Teacher, score_to_gpa_query.c.student_teacher_id == Teacher.id)
            .group_by(
                score_to_gpa_query.c.student_id,
                score_to_gpa_query.c.student_name,
                Teacher.name,
            )
        )

        with Base.session_scope() as session:
            try:
                scores = session.exec(query)
                return [score._mapping for score in scores]

            except SQLAlchemyError as e:
                raise DBAPIError(
                    message="There was an issue trying to calculate the cumulative GPA and teacher name for each student",
                    sql_statement=str(query.compile(dialect=postgresql.dialect())),
                    original_error=str(e),
                )

    def change_teacher(self, student_id: int, teacher_id: int) -> ChangeTeacherResponse:
        """
        Change the teacher assigned to the student

        Args:
            `student_id`: DB ID of student
            `teacher_id`: DB ID of teacher

        Returns:
            `ChangeTeacherResponse`

        Raises:
            `DBRecordNotFoundError`: requested resource does not exist on the DB
            `DBAPIError`: if there was any other issue with the DB request
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
                session.rollback()
                raise DBRecordNotFoundError(
                    message="The requested student cannot be found after the update",
                    sql_statement=str(find_updated_student_query_sql),
                    params=find_updated_student_query_sql.params,
                    original_error=str(e),
                )

            except SQLAlchemyError as e:
                session.rollback()
                raise DBAPIError(
                    message="Exception occured when searching for student after the update to teacher id",
                    sql_statement=str(find_updated_student_query_sql),
                    params=find_updated_student_query_sql.params,
                    original_error=str(e),
                )

    def get_all_cumulative_gpa_and_teacher_name_after(
        self, start_date: datetime
    ) -> list[StudentDataResponse]:
        """
        For each student in the DB, get their the following information for courses that ended during or after the start date:
          (a) name
          (b) cumulative GPA up till this point in time
          (c) teacher name

        Args:
            `start_date`: the earliest date from which you want to start considering student scores

        Returns:
            A list of `StudentDataResponses`

        Raises:
            `DBAPIError`: If there was an issue with the DB request
        """
        score_to_gpa_query = (
            select(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                self.gpa_conversion_scale.c.gpa.label("gpa"),
                Course_Record.grade.label("grade"),
                Student.teacher_id.label("student_teacher_id"),
            )
            .join(Student, Student.id == Course_Record.student_id)
            .join(
                self.gpa_conversion_scale,
                and_(
                    Course_Record.grade >= self.gpa_conversion_scale.c.lower_bound,
                    Course_Record.grade <= self.gpa_conversion_scale.c.upper_bound,
                ),
            )
            .where(Course_Record.end_date >= start_date)
        )

        query = (
            select(
                score_to_gpa_query.c.student_name.label("student_name"),
                Teacher.name.label("teacher_name"),
                func.avg(score_to_gpa_query.c.gpa).label("cumulative_gpa"),
            )
            .join(Teacher, score_to_gpa_query.c.student_teacher_id == Teacher.id)
            .group_by(
                score_to_gpa_query.c.student_id,
                score_to_gpa_query.c.student_name,
                Teacher.name,
            )
        )

        with Base.session_scope() as session:
            try:
                scores = session.exec(query)
                return [score._mapping for score in scores]

            except SQLAlchemyError as e:
                raise DBAPIError(
                    message="There was an issue trying to calculate the cumulative GPA and teacher name for each student when filtering by start date",
                    sql_statement=str(query.compile(dialect=postgresql.dialect())),
                    original_error=str(e),
                )

    def get_all_cumulative_gpa_and_teacher_name_before(
        self, end_date: datetime
    ) -> list[StudentDataResponse]:
        """
        For each student in the DB, get their the following information for courses that ended during or before the start date:
          (a) name
          (b) cumulative GPA up till this point in time
          (c) teacher name

        NOTE: This will exclude students who dont have a course record before `end_date`

        Args:
            `end_date`: the latest date from which you want to start considering student scores

        Returns:
            A list of `StudentDataResponses`

        Raises:
           `DBAPIError`: If there was an issue with the DB request
        """
        score_to_gpa_query = (
            select(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                self.gpa_conversion_scale.c.gpa.label("gpa"),
                Course_Record.grade.label("grade"),
                Student.teacher_id.label("student_teacher_id"),
            )
            .join(Student, Student.id == Course_Record.student_id)
            .join(
                self.gpa_conversion_scale,
                and_(
                    Course_Record.grade >= self.gpa_conversion_scale.c.lower_bound,
                    Course_Record.grade <= self.gpa_conversion_scale.c.upper_bound,
                ),
            )
            .where(Course_Record.end_date <= end_date)
        )

        query = (
            select(
                score_to_gpa_query.c.student_name.label("student_name"),
                Teacher.name.label("teacher_name"),
                func.avg(score_to_gpa_query.c.gpa).label("cumulative_gpa"),
            )
            .join(Teacher, score_to_gpa_query.c.student_teacher_id == Teacher.id)
            .group_by(
                score_to_gpa_query.c.student_id,
                score_to_gpa_query.c.student_name,
                Teacher.name,
            )
        )

        with Base.session_scope() as session:
            try:
                scores = session.exec(query)
                return [score._mapping for score in scores]

            except SQLAlchemyError as e:
                raise DBAPIError(
                    message="There was an issue trying to calculate the cumulative GPA and teacher name for each student when filtering by start date",
                    sql_statement=str(query.compile(dialect=postgresql.dialect())),
                    original_error=str(e),
                )

    def get_all_cumulative_gpa_and_teacher_name_between(
        self, start_date: datetime, end_date: datetime
    ) -> list[StudentDataResponse]:
        """
        For each student in the DB, get their the following information for courses that ended during or before `end_date`, and during or before `start_date`:
          (a) name
          (b) cumulative GPA up till this point in time
          (c) teacher name

        NOTE: This will exclude students who dont have a course record that falls between `start_date` `end_date`

        Args:
            `start_date` : the earliest date from which you want to start considering student scores
            `end_date`: the latest date from which you want to start considering student scores

        Returns:
            A list of `StudentDataResponses`

        Raises:
           `DBAPIError`: If there was an issue with the DB request
        """
        score_to_gpa_query = (
            select(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                self.gpa_conversion_scale.c.gpa.label("gpa"),
                Course_Record.grade.label("grade"),
                Student.teacher_id.label("student_teacher_id"),
            )
            .join(Student, Student.id == Course_Record.student_id)
            .join(
                self.gpa_conversion_scale,
                and_(
                    Course_Record.grade >= self.gpa_conversion_scale.c.lower_bound,
                    Course_Record.grade <= self.gpa_conversion_scale.c.upper_bound,
                ),
            )
            .where(
                and_(
                    Course_Record.end_date <= end_date,
                    Course_Record.end_date >= start_date,
                )
            )
        )

        query = (
            select(
                score_to_gpa_query.c.student_name.label("student_name"),
                Teacher.name.label("teacher_name"),
                func.avg(score_to_gpa_query.c.gpa).label("cumulative_gpa"),
            )
            .join(Teacher, score_to_gpa_query.c.student_teacher_id == Teacher.id)
            .group_by(
                score_to_gpa_query.c.student_id,
                score_to_gpa_query.c.student_name,
                Teacher.name,
            )
        )

        with Base.session_scope() as session:
            try:
                scores = session.exec(query)
                return [score._mapping for score in scores]

            except SQLAlchemyError as e:
                raise DBAPIError(
                    message="There was an issue trying to calculate the cumulative GPA and teacher name for each student when filtering by start date",
                    sql_statement=str(query.compile(dialect=postgresql.dialect())),
                    original_error=str(e),
                )
