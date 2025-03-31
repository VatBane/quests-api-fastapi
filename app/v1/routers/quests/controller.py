from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.schemas import QuestOrm, TaskOrm
from v1.exceptions.exceptions import DuplicateError
from v1.routers.quests.models.quest import QuestOutput, QuestInput
from v1.routers.quests.models.tasks import TaskOutput


class QuestController:
    def __init__(self,
                 session: AsyncSession,
                 ):
        self.session = session

    async def get_all_quests(self,
                             limit: int = 20,
                             offset: int = 0
                             ) -> list[QuestOutput]:
        query = select(QuestOrm).limit(limit).offset(offset).order_by(QuestOrm.id)
        result = await self.session.execute(query)
        result = [QuestOutput.model_validate(r) for r in result]

        return result

    async def create_quest(self,
                           quest: QuestInput
                           ) -> QuestOutput:
        quest_db = QuestOrm(**quest.model_dump(exclude={"tasks"}))

        try:
            self.session.add(quest_db)
            await self.session.flush()
            await self.session.refresh(quest_db)
        except IntegrityError:
            raise DuplicateError("Quest with this name already exists!")

        try:
            tasks = [TaskOrm(quest_id=quest_db.id, **task.model_dump()) for task in quest.tasks]
            self.session.add_all(tasks)
            await self.session.flush()
            [await self.session.refresh(task) for task in tasks]
        except IntegrityError:
            raise DuplicateError("Each question should be unique!")

        result = QuestOutput.model_validate(quest_db)
        result.tasks = [TaskOutput.model_validate(t) for t in tasks]

        return result
