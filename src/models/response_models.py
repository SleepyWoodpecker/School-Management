from pydantic import BaseModel, ConfigDict
from humps import camelize


def to_camel(string: str) -> str:
    return camelize(string)


class CamelResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class PingResponse(CamelResponse):
    pong: bool
    database_connected: bool


class StudentDataResponse(CamelResponse):
    student_name: str
    cumulative_gpa: float
    teacher_name: str


class ChangeTeacherResponse(CamelResponse):
    student_name: str
    teacher_name: str
