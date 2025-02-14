from fastapi import FastAPI, status, Request, HTTPException, Depends
from contextlib import asynccontextmanager

from models.response_models import PingResponse, StudentDataResponse
from DB import init_db, StudentDB, DBConnectionError


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
    """Dependency that verifies DB status for protected routes"""
    if not request.app.state.db_connected:
        raise HTTPException(
            status_code=503, detail="Service unavailable - Database connection failed"
        )
    return True


@app.get("/ping", status_code=status.HTTP_200_OK)
def pong(request: Request) -> PingResponse:
    return {"pong": True, "database_connected": request.app.state.db_connected}


@app.get(
    "/get-all-student-data",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_db_connection)],
)
def get_student_data() -> list[StudentDataResponse]:
    """For all students in the DB, get back their name, cumulative GPA and teacher's name"""
    all_student_data = student_db.get_all_cumulative_gpa_and_teacher_name()
    return all_student_data
