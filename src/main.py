from fastapi import FastAPI, status, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Callable
from contextlib import asynccontextmanager

from models.response_models import (
    PingResponse,
    StudentDataResponse,
    ChangeTeacherResponse,
)
from models.request_models import ChangeTeacherRequest
from DB import init_db, StudentDB, DBConnectionError, DBAPIError, DBRecordNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """manages what functions run on app startup and what funcitions run on app teardown"""
    try:
        init_db()
        app.state.db_connected = True
    except DBConnectionError as e:
        app.state.db_connected = False
        print("Trouble connecting to DB :(")

    yield ()


app = FastAPI(lifespan=lifespan)
student_db = StudentDB()


def verify_db_connection(request: Request):
    """Dependency that verifies DB status for routes"""
    if not request.app.state.db_connected:
        raise HTTPException(
            status_code=503, detail="Service unavailable - Database connection failed"
        )
    return True


def create_exception_handler(
    status_code: int, initial_detials: str
) -> Callable[[Request, DBAPIError], JSONResponse]:
    detail = {"message": initial_detials}

    def exception_handler(_: Request, exc: DBAPIError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message

        # TODO: log the error
        print("HERE ", exc.sql_statement, exc.params)
        return JSONResponse(
            status_code=status_code, content={"details": detail["message"]}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=DBRecordNotFoundError,
    handler=create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detials="The record you requested cannot be found",
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=DBAPIError,
    handler=create_exception_handler(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        initial_detials="We are experiencing some trouble performing our DB operations",
    ),
)


@app.get("/ping", status_code=status.HTTP_200_OK)
def pong(request: Request) -> PingResponse:
    return {"pong": True, "database_connected": request.app.state.db_connected}


@app.get(
    "/students",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_db_connection)],
)
def get_student_data() -> list[StudentDataResponse]:
    """For all students in the DB, get back their name, cumulative GPA and teacher's name"""
    all_student_data = student_db.get_all_cumulative_gpa_and_teacher_name()
    return all_student_data


@app.post(
    "/student/change-teacher",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_db_connection)],
)
def change_teacher_data(req_body: ChangeTeacherRequest) -> ChangeTeacherResponse:
    """
    Changes the teacher that is assigned to the student, returning the new reocrd of the student-teacher pair upon a successful update

    Here, the API contract asks for the student's ID and the new teacher's ID because they can uniquely identify the student and teacher.
    It is also likely that the frontend has that kind of data encoded into them already.
    """
    updated_student = student_db.change_teacher(
        req_body.student_id, req_body.new_teacher_id
    )
    return updated_student
