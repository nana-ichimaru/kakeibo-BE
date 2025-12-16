from kakeibo_be.models.response.v1.base import BaseResponse


class ErrorResponse(BaseResponse):
    detail: str
