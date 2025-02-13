from fastapi import FastAPI, status
from models.response_models import PingResponse

app = FastAPI()


@app.get("/ping", status_code=status.HTTP_200_OK)
def pong() -> PingResponse:
    return {"pong": True}
