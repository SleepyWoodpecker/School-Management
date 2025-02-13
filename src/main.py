from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from models.response_models import PingResponse
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
