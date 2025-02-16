from fastapi import FastAPI, status, Request, HTTPException, Depends, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Callable
from contextlib import asynccontextmanager
from typing import Annotated
import logging, os
from dotenv import load_dotenv, find_dotenv

from models.response_models import (
    PingResponse,
    ChangeTeacherResponse,
    RecordNotFoundResponse,
    InvalidParamsResponse,
    StudentDataListResponse,
    BadRequestResponse,
)
from models.request_models import ChangeTeacherRequest
from validators import validate_date
from DB import init_db, StudentDB, DBConnectionError, DBAPIError, DBRecordNotFoundError

load_dotenv(find_dotenv())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """manages what functions run on app startup and what funcitions run on app teardown"""
    if not os.path.exists(f"""./{os.getenv("LOGGING_FOLDER")}"""):
        os.makedirs(f"""{os.getenv("LOGGING_FOLDER")}""", exist_ok=True)
    try:
        logging.basicConfig(
            filename=f"""./{os.getenv("LOGGING_FOLDER")}/{os.getenv("LOG_FILE")}""",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    except FileNotFoundError:
        print("logging cannot be set up")

    try:
        init_db()
        app.state.db_connected = True
    except DBConnectionError as e:
        app.state.db_connected = False
        logging.critical("DB CONNECTION CANNOT BE ESTABLISHED")
        print("Trouble connecting to DB :(")

    yield ()


app = FastAPI(lifespan=lifespan)

student_db = StudentDB()


def verify_db_connection(request: Request):
    """Dependency that verifies DB status for routes"""
    if not request.app.state.db_connected:
        logging.critical("DB CONNECTION CANNOT BE ESTABLISHED")
        raise HTTPException(
            status_code=503, detail="Service unavailable - Database connection failed"
        )
    return True


# general exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError):
    logging.info(
        f"Invalid request params | {req.url} | {(await req.body()).decode()} | {req.query_params}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request parameters",
            "params": exc.body,
            "ok": False,
        },
    )


# DB exception handlers
def create_exception_handler(
    status_code: int, initial_detials: str
) -> Callable[[Request, DBAPIError], JSONResponse]:
    detail = {"message": initial_detials}

    def exception_handler(_: Request, exc: DBAPIError) -> JSONResponse:

        logging.info(
            f"Unsuccessful DB operation | {exc.message} | {exc.sql_statement} | {exc.params} | {exc.original_error}"
        )
        print("HERE ", exc.sql_statement, exc.params)
        return JSONResponse(
            status_code=status_code, content={"details": detail["message"], "ok": False}
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
    return {
        "ok": True,
        "pong": True,
        "database_connected": request.app.state.db_connected,
    }


@app.get(
    "/students",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_db_connection)],
    responses={
        status.HTTP_200_OK: {
            "model": StudentDataListResponse,
            "description": "Returns a list of all the student data requested. If a startDate and or endDate were provided, only student data from that period of time would be considered",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequestResponse,
            "description": "Ordering of dates is incorrect",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": InvalidParamsResponse,
            "description": "Dates were not formatted in the DD-MM-YYYY style specified",
        },
    },
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
) -> StudentDataListResponse:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Start date should not come before the end date. startDate: {start_date}, endDate: {end_date}",
        )

    student_data_response = []

    if start_date and end_date:
        student_data_response = (
            student_db.get_all_cumulative_gpa_and_teacher_name_between(
                start_date, end_date
            )
        )

    elif start_date:
        student_data_response = (
            student_db.get_all_cumulative_gpa_and_teacher_name_after(start_date)
        )

    elif end_date:
        student_data_response = (
            student_db.get_all_cumulative_gpa_and_teacher_name_before(end_date)
        )

    else:
        student_data_response = student_db.get_all_cumulative_gpa_and_teacher_name()

    return {"ok": True, "student_data": student_data_response}


@app.post(
    "/students/change-teacher",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_db_connection)],
    responses={
        status.HTTP_200_OK: {
            "model": ChangeTeacherResponse,
            "description": "Teacher changed successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": RecordNotFoundResponse,
            "description": "raised when either the requested student / teacher cannot be found",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": InvalidParamsResponse,
            "description": "raised when the request parameters, student_id / new_teacher_id are invalid",
        },
    },
)
# Here, the API contract asks for the student's ID and the new teacher's ID because they can uniquely identify the student and teacher.
#  It is also likely that the frontend has that kind of data encoded into them already.
def change_teacher_data(req_body: ChangeTeacherRequest) -> ChangeTeacherResponse:
    """
    Changes the teacher that is assigned to the student, returning the new record of the student-teacher pair upon a successful update

    Body params:

        student_id: the id of the student who you want to change a teacher for

        new_teacher_id: the id of the new teacher that you want to assign to the student

    """
    updated_student = student_db.change_teacher(
        req_body.student_id, req_body.new_teacher_id
    )
    updated_student["ok"] = True

    return updated_student


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3003)
