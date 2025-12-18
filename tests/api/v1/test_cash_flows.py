from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import RollbackTracker


def test_create_cash_flow(client: TestClient) -> None:
    body = {
        "title": "もも",
        "type": "expense",
        "recordedAt": "2025-12-01",
        "amount": 200,
    }
    response = client.post(
        "/api/v1/cash-flows",
        json=body,
    )
    assert response.status_code == 200
    result: dict = response.json()
    assert result["id"]
    assert result["title"] == body["title"]
    assert result["type"] == body["type"]
    assert result["recordedAt"] == body["recordedAt"]
    assert result["amount"] == body["amount"]


def test_create_cash_flow_error(
    client_with_commit_error: TestClient,
    rollback_tracker: RollbackTracker,
    db_session_commit_error: Session,
) -> None:
    body = {
        "title": "もも",
        "type": "expense",
        "recordedAt": "2025-12-01",
        "amount": 200,
    }
    response = client_with_commit_error.post(
        "/api/v1/cash-flows",
        json=body,
    )
    result: dict = response.json()
    assert rollback_tracker.called
    assert response.status_code == 500
    assert result["detail"] == "システムエラーが発生しました。"
