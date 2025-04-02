import json
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, field_serializer, field_validator, ConfigDict, model_validator

from v1.models.enums.task_type import TaskType


class TaskBase(BaseModel):
    question: Annotated[str, Field(min_length=1)]
    responses: list[str]
    answers: Annotated[list[str], Field(min_length=1)]

    @field_serializer('responses', 'answers')
    def serialize_responses_and_answers(self, value: list[str]):
        return json.dumps(value)

    @field_validator('responses', 'answers', mode='before')
    @classmethod
    def validate_responses_and_answers(cls, value: str | list[str]):
        if isinstance(value, str):
            return json.loads(value)

        return value


class TextTaskInput(TaskBase):
    type: Literal[TaskType.TEXT]

    @model_validator(mode='after')
    def check_response_and_answer(self) -> Self:
        if len(self.responses) > 0:
            raise ValueError("Text questions do not accept any response variants!")
        if len(self.answers) != 1:
            raise ValueError("Text questions accept only 1 correct answer!")

        return self


class SingleTaskInput(TaskBase):
    type: Literal[TaskType.SINGLE]

    @model_validator(mode='after')
    def check_response_and_answer(self) -> Self:
        if len(self.responses) < 2:
            raise ValueError("Single questions accept at least 2 response variants!")
        if len(self.answers) != 1:
            raise ValueError("Single questions accept only 1 correct answer!")

        return self


class ImageTaskInput(TaskBase):
    type: Literal[TaskType.IMAGE]

    @model_validator(mode='after')
    def check_response_and_answer(self) -> Self:
        if len(self.responses) < 2:
            raise ValueError("Image questions accept at least 2 response variants!")
        if len(self.answers) != 1:
            raise ValueError("Image questions accept only 1 correct answer!")

        return self

class MultipleTaskInput(TaskBase):
    type: Literal[TaskType.MULTIPLE]

    @model_validator(mode='after')
    def check_response_and_answer(self) -> Self:
        if len(self.responses) < 2:
            raise ValueError("Multiple questions accept at least 2 response variants!")
        if len(self.answers) == 0:
            raise ValueError("Multiple questions accept at least 1 correct answer!")


class TaskOutput(TaskBase):
    id: int = Field(gt=0)

    model_config = ConfigDict(from_attributes=True)
