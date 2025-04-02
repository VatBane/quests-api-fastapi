from starlette import status


class CustomError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ValidationError(CustomError):
    status_code = status.HTTP_400_BAD_REQUEST


class DuplicateError(CustomError):
    status_code = status.HTTP_409_CONFLICT


class ResourceNotFoundError(CustomError):
    status_code = status.HTTP_404_NOT_FOUND
