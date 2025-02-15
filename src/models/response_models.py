from pydantic import BaseModel, ConfigDict
from humps import camelize


def to_camel(string: str) -> str:
    return camelize(string)


class CamelResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ResponseModel(CamelResponse):
    ok: bool


class PingResponse(ResponseModel):
    pong: bool
    database_connected: bool


class StudentData(CamelResponse):
    student_name: str
    cumulative_gpa: float
    teacher_name: str


class StudentDataResponse(ResponseModel, StudentData):
    pass


class StudentDataListResponse(ResponseModel):
    student_data: list[StudentData]


class ChangeTeacherResponse(ResponseModel):
    student_id: int
    student_name: str
    updated_teacher_id: int
    updated_teacher_name: str


class InvalidParamsResponse(ResponseModel):
    detail: str
    params: str


class BadRequestResponse(ResponseModel):
    pass


class RecordNotFoundResponse(ResponseModel):
    details: str
