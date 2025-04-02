from datetime import datetime

from sqlalchemy import Integer, String, PrimaryKeyConstraint, UniqueConstraint, Text, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column

from v1.database.functions import utc_now
from v1.models.enums.quest_status import QuestStatus
from v1.models.enums.task_type import TaskType


class Base(DeclarativeBase):
    pass


class QuestOrm(Base):
    __tablename__ = "quest"

    id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=True)
    # questions_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    # completions_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='quest_pkey'),
        UniqueConstraint('name', name='quest_name_uc'),
    )


class TaskOrm(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer)
    quest_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False, default=TaskType.TEXT,
                                      server_default=TaskType.TEXT)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    responses: Mapped[str] = mapped_column(Text, nullable=False)
    answers: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='task_pkey'),
        ForeignKeyConstraint(['quest_id'], ['quest.id'], name='task_quest_fkey',
                             ondelete="CASCADE", onupdate="CASCADE"),
        UniqueConstraint('quest_id', 'question', name='task_question_uc'),
    )


class CompletionOrm(Base):
    __tablename__ = "completion"

    id: Mapped[int] = mapped_column(Integer)
    quest_id: Mapped[int] = mapped_column(Integer)
    user: Mapped[str] = mapped_column(Text, nullable=False)
    time_took: Mapped[int] = mapped_column(Integer, nullable=False)
    rate: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[int] = mapped_column(String(16), default=QuestStatus.IN_PROGRESS,
                                        server_default=QuestStatus.IN_PROGRESS)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=utc_now())
    submitted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True, onupdate=utc_now())

    __table_args__ = (
        PrimaryKeyConstraint('id', name="completion_pkey"),
        ForeignKeyConstraint(['quest_id'], ['quest.id'], name="completion_quest_fkey",
                             ondelete="CASCADE", onupdate="CASCADE"),
        UniqueConstraint('quest_id', 'user', name="completion_quest_user_uc"),
    )


class TaskCompletionOrm(Base):
    __tablename__ = 'task_completion'

    id: Mapped[int] = mapped_column(Integer)
    completion_id: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[int] = mapped_column(Integer)
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id", name='task_completion_pkey'),
        ForeignKeyConstraint(["completion_id"], ['completion.id'], name="task_completion_completion_fkey",
                             ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint(['task_id'], ['task.id'], name="task,completion_task_fkey",
                             ondelete="CASCADE", onupdate="CASCADE"),
        UniqueConstraint('completion_id', 'task_id', name="task_completion_uc"),
    )
