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
    tasks: list[TaskOutput] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
