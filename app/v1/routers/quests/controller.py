from sqlalchemy import select, func, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.schemas import QuestOrm, TaskOrm, CompletionOrm
from v1.exceptions.exceptions import DuplicateError, ValidationError, ResourceNotFoundError
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
                                    sorts: list[Sort],
                                    pagination: Pagination) -> list[QuestOutput]:
        """
        Returns list of quests
        :param sorts: info how to sort response
        :param pagination: pagination details
        :return: list of quest
        """
        # validate if user provided wrong columns
        if any(sort.column not in QuestOutput.get_fields() for sort in sorts):
            raise ValidationError("Sort by non-existing field!")

        # define sort order
        order_by = []
        for sort in sorts:
            sort.column = getattr(QuestOrm, sort.column, sort.column)
            order_by.append(asc(sort.column) if sort.order == 'asc' else desc(sort.column))

        # query objects
        query = (select(QuestOrm,
                        func.count(TaskOrm.id).label('questionsNumber'),
                        func.count(CompletionOrm.id).label('completionsNumber'))
                 .join(TaskOrm, TaskOrm.quest_id == QuestOrm.id, isouter=True)
                 .join(CompletionOrm, CompletionOrm.quest_id == QuestOrm.id, isouter=True)
                 .group_by(QuestOrm)
                 .limit(pagination.limit)
                 .offset(pagination.offset)
                 .order_by(*order_by)
                 )

        result = await self.session.execute(query)
        result = result.all()

        # create result and send it back
        result = [
            QuestOutput.model_validate({
                "id": quest.id,
                "name": quest.name,
                "description": quest.description,
                "questionsNumber": questions_number,
                "completionNumber": completions_number,
            })
            for (quest, questions_number, completions_number) in result]

        return result

    async def create_quest(self,
                           quest: QuestInput
                           ) -> QuestOutputExtended:
        """
        Creates new instances of Quest and Task
        :param quest: quest info and tasks
        :return: same information with ids
        """
        # save Quest instance
        quest_db = QuestOrm(**quest.model_dump(exclude={"tasks"}))

        try:
            self.session.add(quest_db)
            await self.session.flush()
            await self.session.refresh(quest_db)
        except IntegrityError:
            raise DuplicateError("Quest with this name already exists!")

        # save Task instances
        try:
            tasks = [TaskOrm(quest_id=quest_db.id, order=order, **task.model_dump())
                     for order, task in enumerate(quest.tasks)]
            self.session.add_all(tasks)
            await self.session.flush()
            [await self.session.refresh(task) for task in tasks]
        except IntegrityError:
            raise DuplicateError("Each question should be unique!")

        # return result
        result = QuestOutputExtended.model_validate({
            "id": quest_db.id,
            "name": quest_db.name,
            "description": quest_db.description,
            "tasks": [TaskOutput.model_validate(t) for t in tasks],
        })

        return result

    async def get_quest_info(self, quest_id: int):
        query = select(QuestOrm).where(QuestOrm.id == quest_id)
        quest = await self.session.execute(query)
        quest = quest.scalar()

        if not quest:
            raise ResourceNotFoundError("Quest with given id not exist!")

        query = select(TaskOrm).where(TaskOrm.quest_id == quest_id).order_by(asc(TaskOrm.order),
                                                                             asc(TaskOrm.id))
        tasks = await self.session.execute(query)
        tasks = tasks.scalars().all()
        tasks = [TaskOutput.model_validate(task) for task in tasks]

        quest = QuestOutputExtended.model_validate({
            "id": quest.id,
            "name": quest.name,
            "description": quest.description,
            "tasks": tasks})

        return quest
