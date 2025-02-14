from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from models.response_models import PingResponse, StudentDataResponse
from DB.DB import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """manages what functions run on app startup and what funcitions run on app teardown"""
    init_db()
    yield ()


app = FastAPI(lifespan=lifespan)


@app.get("/ping", status_code=status.HTTP_200_OK)
def pong() -> PingResponse:
    return {"pong": True}


@app.get("/get-all-student-data", status_code=status.HTTP_200_OK)
def get_student_data() -> list[StudentDataResponse]:
    return [
        {
            "student_name": "Jameson",
            "cumulative_gpa": 1.7666666666666666,
            "teacher_name": "Mr Anderson",
        },
        {"student_name": "Katie", "cumulative_gpa": 4.0, "teacher_name": "Ms Rita"},
    ]
