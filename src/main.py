from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from models.response_models import PingResponse, StudentDataResponse
from DB.DB import init_db
from DB import StudentDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    """manages what functions run on app startup and what funcitions run on app teardown"""
    init_db()
    yield ()


app = FastAPI(lifespan=lifespan)
student_db = StudentDB()


@app.get("/ping", status_code=status.HTTP_200_OK)
def pong() -> PingResponse:
    return {"pong": True}


@app.get("/get-all-student-data", status_code=status.HTTP_200_OK)
def get_student_data() -> list[StudentDataResponse]:
    all_student_data = student_db.get_all_cumulative_gpa_and_teacher_name()
    return all_student_data
