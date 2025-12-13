from fastapi import HTTPException


class BusinessException(HTTPException):
    # self：クラス自身
    def __init__(self, message: str) -> None:
        # super：親クラス（＝HTTPException）
        super().__init__(status_code=422, detail=message)