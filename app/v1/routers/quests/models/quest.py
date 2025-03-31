from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict

from v1.routers.quests.models.tasks import TextTaskInput, SingleTaskInput, MultipleTaskInput, ImageTaskInput, TaskOutput


class QuestBase(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(default="")


class QuestInput(QuestBase):
    tasks: list[Annotated[TextTaskInput | SingleTaskInput | MultipleTaskInput | ImageTaskInput, Field(discriminator='type')]]


class QuestOutput(QuestBase):
    id: int = Field(gt=0)
    questions_number: int = Field(alias="questionsNumber", gt=0, default=1)
    completions_number: int = Field(alias="completionsNumber", ge=0, default=0)

    model_config = ConfigDict(from_attributes=True)
