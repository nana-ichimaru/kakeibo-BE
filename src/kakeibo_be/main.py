from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kakeibo_be.api import router as api_router
from kakeibo_be.core.connection import FE_BASE_URL
from kakeibo_be.handlers.server_exception_handler import handler

app = FastAPI()


# フロンドエンドと繋げる設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FE_BASE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

app.add_exception_handler(Exception, handler)
