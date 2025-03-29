from enum import Enum


class TaskType(str, Enum):
    TEXT = "text"
    SINGLE = "single"
    MULTIPLE = "multiple"
    IMAGE = "image"
