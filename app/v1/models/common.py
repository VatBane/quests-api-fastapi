from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(default=20, gt=0)
    offset: int = Field(default=0, ge=0)


class Sort(BaseModel):
    column: Annotated[str, Field(default="id")]
    order: Literal["asc", "desc"]
