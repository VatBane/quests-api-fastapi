from sqlalchemy import select, func, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from v1.database.schemas import QuestOrm, TaskOrm, CompletionOrm
from v1.exceptions.exceptions import DuplicateError
from v1.models.common import Sort, Pagination
from v1.routers.quests.models.quest import QuestOutput, QuestInput, QuestOutputExtended
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
        query = (select(QuestOrm,
                        func.count(TaskOrm.id).label('questions_number'),
                        func.count(CompletionOrm.id).label('completions_number'))
                 .outerjoin(TaskOrm, TaskOrm.quest_id == QuestOrm.id)
                 .outerjoin(CompletionOrm, CompletionOrm.quest_id == QuestOrm.id)
                 .group_by(QuestOrm.id)
                 .limit(limit)
                 .offset(offset)
                 .order_by(QuestOrm.id)
                 )
        result = await self.session.execute(query)
        result = result.all()

        result = [
            QuestOutput.model_validate({
                "id": quest.id,
                "name": quest.name,
                "description": quest.description,
                "questions_number": questions_number,
                "completion_number": completions_number,
            })
            for quest, questions_number, completions_number in result]

        return result

    async def get_quests_by_filters(self,
                                    sort: Sort,
                                    pagination: Pagination):
        order_by = asc(*sort.columns) if sort.order == 'asc' else desc(*sort.columns)

        query = (select(QuestOrm,
                        func.count(TaskOrm.id).label('questions_number'),
                        func.count(CompletionOrm.id).label('completions_number'))
                 .outerjoin(TaskOrm, TaskOrm.quest_id == QuestOrm.id)
                 .outerjoin(CompletionOrm, CompletionOrm.quest_id == QuestOrm.id)
                 .group_by(QuestOrm)
                 .limit(pagination.limit)
                 .offset(pagination.offset)
                 .order_by(order_by)
                 )

        query_builder = QueryBuilder()
        query_builder.select([QuestOrm, func.count(TaskOrm.id).label('questions_number'),
                              func.count(CompletionOrm.id).label('completions_number')])

        result = await self.session.execute(query)
        result = result.all()

        result = [
            QuestOutput.model_validate({
                "id": quest.id,
                "name": quest.name,
                "description": quest.description,
                "questions_number": questions_number,
                "completion_number": completions_number,
            })
            for quest, questions_number, completions_number in result]

        return result

    async def create_quest(self,
                           quest: QuestInput
                           ) -> QuestOutputExtended:
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

        result = QuestOutputExtended.model_validate({
            "id": quest_db.id,
            "name": quest_db.name,
            "description": quest_db.description,
            "tasks": [TaskOutput.model_validate(t) for t in tasks],
        })

        return result
