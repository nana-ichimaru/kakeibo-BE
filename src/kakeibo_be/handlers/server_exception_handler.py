from fastapi.requests import Request
from fastapi.responses import JSONResponse

from kakeibo_be.models.response.v1.error import ErrorResponse


def handler(request: Request, exc: Exception) -> JSONResponse:
    response_body = ErrorResponse(detail="システムエラーが発生しました。")
    return JSONResponse(
        status_code=500,
        # JOSON型にdump
        content=response_body.model_dump(),
    )
    
    




