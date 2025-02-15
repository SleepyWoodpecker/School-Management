from faker import Faker
from pprint import pprint
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from DB import Teacher, Student, Course_Record, init_db
from DB.Base import Base


def randomly_seed_db():
    fake = Faker()
    init_db()
    with Base.session_scope() as session:
        try:
            # create 2 fake teachers
            teachers = []
            teacher_ids = []
            for _ in range(2):
                teacher = Teacher(name=fake.name())
                session.add(teacher)
                session.commit()
                session.refresh(teacher)

                teacher_ids.append(teacher.id)
                teachers.append(teacher)

            print("Finished uploading teachers:")
            pprint(teachers)

            # create 10 fake students
            students = []
            student_ids = []
            for teacher_id in teacher_ids:
                for _ in range(5):
                    student = Student(name=fake.name(), teacher_id=teacher_id)
                    session.add(student)
                    session.commit()
                    session.refresh(student)

                    student_ids.append(student.id)
                    students.append(student)

            print("Finished uploading students:")
            pprint(students)

            dates = []
            for year in range(2021, 2025):
                for month, day in ((4, 1), (11, 1)):
                    dates.append(datetime(year, month, day).strftime("%Y-%m-%d"))

            course_records = []
            for student_id in student_ids:
                for date in dates:
                    course_record = Course_Record(
                        student_id=student_id,
                        end_date=date,
                        grade=fake.pyfloat(min_value=0.0, max_value=100.0),
                    )
                    session.add(course_record)
                    session.commit()
                    session.refresh(course_record)

                    course_records.append(course_record)

            print("finished uploading course records: ")
            pprint(course_records)
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()


if __name__ == "__main__":
    randomly_seed_db()
