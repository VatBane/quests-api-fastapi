from sqlalchemy import select, func, asc, desc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from v1.database.schemas import QuestOrm, TaskOrm, CompletionOrm
from v1.exceptions.exceptions import DuplicateError, ValidationError
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
                                    pagination: Pagination) -> list[QuestOutput]:
        """
        Returns list of quests
        :param sort: info how to sort response
        :param pagination: pagination details
        :return: list of quest
        """
        # validate if user provided wrong columns
        if any(col not in QuestOutput.get_fields() for col in sort.columns):
            raise ValidationError("Sort by non-existing field!")

        # define sort order
        sort.columns = [getattr(QuestOrm, col, col) for col in sort.columns]
        if sort.order == 'asc':
            order_by = [asc(col) for col in sort.columns]
        else:
            order_by = [desc(col) for col in sort.columns]

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
            tasks = [TaskOrm(quest_id=quest_db.id, **task.model_dump()) for task in quest.tasks]
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
