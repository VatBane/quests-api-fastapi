from typing import Annotated

from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import get_session
from v1.exceptions.exceptions import CustomError
from v1.models.common import Pagination, Sort
from v1.routers.quests.controller import QuestController
from v1.routers.quests.models.quest import QuestInput, QuestOutput

quest_router = APIRouter(tags=["Quest Management"])


@quest_router.get('/', deprecated=True)
async def get_all_quests(session: Annotated[AsyncSession, Depends(get_session)],
                         limit: Annotated[int, Query(gt=0)] = 20,
                         offset: Annotated[int, Query(ge=0)] = 0,
                         ):
    controller = QuestController(session=session)
    result = await controller.get_all_quests(limit=limit, offset=offset)

    return result


@quest_router.post('/')
async def create_quest(session: Annotated[AsyncSession, Depends(get_session)],
                       quest: Annotated[QuestInput, Body()],
                       ):
    controller = QuestController(session=session)

    try:
        result = await controller.create_quest(quest=quest)
        await session.commit()
    except CustomError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    return result


@quest_router.post('/by_filters')
async def get_quests_by_filters(session: Annotated[AsyncSession, Depends(get_session)],
                                sorts: Annotated[list[Sort], Body()],
                                pagination: Annotated[Pagination, Body()],
                                ) -> list[QuestOutput]:
    controller = QuestController(session=session)

    try:
        result = await controller.get_quests_by_filters(sorts=sorts, pagination=pagination)
    except CustomError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    return result
