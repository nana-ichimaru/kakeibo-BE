from fastapi import FastAPI

from kakeibo_be.api import router as api_router
from kakeibo_be.handlers.server_exception_handler import handler

app = FastAPI()

app.include_router(api_router, prefix="/api")

app.add_exception_handler(Exception, handler)