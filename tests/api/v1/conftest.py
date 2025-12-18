from collections.abc import Generator

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from kakeibo_be.main import app
from kakeibo_be.models.db.base import get_db


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_with_commit_error(db_session_commit_error: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session_commit_error

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app, raise_server_exceptions=False)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
