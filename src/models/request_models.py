from humps import camelize, decamelize
from pydantic import BaseModel, ConfigDict, model_validator


def to_snake(string: str) -> str:
    return decamelize(string)


def to_camel(string: str) -> str:
    return camelize(string)


class CamelRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def check_card_number_not_present(cls, data: any) -> any:
        if isinstance(data, dict):
            return {to_snake(k): v for k, v in data.items()}
        return data


class ChangeTeacherRequest(CamelRequest):
    student_id: int
    new_teacher_id: int
