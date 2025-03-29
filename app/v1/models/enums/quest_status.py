from enum import Enum


class QuestStatus(str, Enum):
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    ABORTED = "aborted"
