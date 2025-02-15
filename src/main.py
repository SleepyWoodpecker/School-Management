from fastapi import FastAPI, status, Request, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Callable
from contextlib import asynccontextmanager
from typing import Annotated
from datetime import datetime

from models.response_models import (
    PingResponse,
    StudentDataResponse,
    ChangeTeacherResponse,
)
from models.request_models import ChangeTeacherRequest
from validators import validate_date
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
def get_student_data(
    start_date: Annotated[
        str,
        Query(alias="startDate", description="Format: DD-MM-YYYY"),
    ] = None,
    end_date: Annotated[
        str,
        Query(alias="endDate", description="Format: DD-MM-YYYY"),
    ] = None,
) -> list[StudentDataResponse]:
    """
    For all students in the DB, get back their name, cumulative GPA and teacher's name

    When provided with the optional startDate and endDate arguments, filter course records based on the end date of that course. This is so that all course records can be meaningfully included in the student's cumulative GPA calculation

    Args:

        startDate: the earliest record that you want to take into consideration

        endDate: the latest record that you want to take into consideration

    Returns:

        If neither startDate nor endDate are provided, all student course records that will be considered

        If only startDate is provided, only courses that ended after the start date are considered

        If only endDate is provided, only course that ended before the endDate are considered

        If both startDate and endDate are provided, only course records that ended between the startDate and the endDate are considered
    """
    # ideally, this could have been a dependency, but I could not combine a dependency and a query, so this is in the route handling logic instead
    start_date = validate_date(start_date)
    end_date = validate_date(end_date)

    if start_date and end_date and start_date > end_date:
        # TODO: add documentation for this error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Start date should not come before the end date. startDate: {start_date}, endDate: {end_date}",
        )

    if start_date and end_date:
        pass

    elif start_date:
        pass

    elif end_date:
        pass

    else:
        return student_db.get_all_cumulative_gpa_and_teacher_name()


@app.post(
    "/student/change-teacher",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_db_connection)],
)
# Here, the API contract asks for the student's ID and the new teacher's ID because they can uniquely identify the student and teacher.
#  It is also likely that the frontend has that kind of data encoded into them already.
def change_teacher_data(req_body: ChangeTeacherRequest) -> ChangeTeacherResponse:
    """
    Changes the teacher that is assigned to the student, returning the new record of the student-teacher pair upon a successful update
    """
    updated_student = student_db.change_teacher(
        req_body.student_id, req_body.new_teacher_id
    )
    return updated_student
