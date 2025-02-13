from pydantic import BaseModel


class PingResponse(BaseModel):
    pong: bool
