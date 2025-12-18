from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import RollbackTracker
from tests.factories.cash_flow import create_cash_flow


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
    result = response.json()
    assert result["id"]
    assert result["title"] == body["title"]
    assert result["type"] == body["type"]
    assert result["recordedAt"] == body["recordedAt"]
    assert result["amount"] == body["amount"]


def test_create_cash_flow_error(
    client_with_commit_error: TestClient,
    rollback_tracker: RollbackTracker,
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
    result = response.json()
    assert rollback_tracker.called
    assert response.status_code == 500
    assert result["detail"] == "システムエラーが発生しました。"


def test_get_cash_flow(client: TestClient, db_session: Session) -> None:
    for i in range(1, 13):
        mock_cach_flow = {
            "id": i,
            "title": f"もも_{i}",
            "recorded_at": date(year=2025, month=i, day=1),
            "amount": 100 * i,
        }
        create_cash_flow(db_session, **mock_cach_flow)

    target_month_number = 12
    target_params = {"target_month": f"2025-{target_month_number}-01"}

    response = client.get(
        "/api/v1/cash-flows",
        params=target_params
    )

    target_id = target_month_number 

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == target_id
    assert result[0]["title"] == f"もも_{target_id}"
    assert result[0]["recordedAt"] == f"2025-{target_month_number}-01"
    assert result[0]["amount"] == 100 * target_id

    # assert [item["title"] for item in result] == ["もも_12"]
    # all は 全部Trueか？ を見る
    # 文字列が指定した接頭辞（prefix）で始まるかを判定します
    # assert all(item["recordedAt"].startswith("2025-12") for item in result)


def test_get_cash_flow_no_data(client: TestClient, db_session: Session) -> None:
    target_params = {"target_month": "2025-12-01"}

    response = client.get(
        "/api/v1/cash-flows",
        params=target_params
    )

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 0
    assert type(result) is list

def test_update_cash_flow(client: TestClient, db_session: Session) -> None:
    mock_cach_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    body = {
        "title": "もも",
        "type": "income",
        "recordedAt": "2025-12-01",
        "amount": 400,
    }

    cash_flow_id = 1
    response = client.put(
        f"/api/v1/cash-flows/{cash_flow_id}",
        json=body,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"]
    assert result["title"] == body["title"]
    assert result["type"] == body["type"]
    assert result["recordedAt"] == body["recordedAt"]
    assert result["amount"] == body["amount"]


def test_update_cash_flow_not_found(client: TestClient, db_session: Session) -> None:
    mock_cach_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    body = {
        "title": "もも",
        "type": "income",
        "recordedAt": "2025-12-01",
        "amount": 400,
    }

    cash_flow_id = 2
    response = client.put(
        f"/api/v1/cash-flows/{cash_flow_id}",
        json=body,
    )

    assert response.status_code == 422
    result = response.json()
    assert result["detail"] == "CashFlow not found!"


def test_update_cash_flow_error(client_with_commit_error: TestClient,
    rollback_tracker: RollbackTracker,db_session: Session) -> None:
    mock_cach_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    body = {
        "title": "もも",
        "type": "income",
        "recordedAt": "2025-12-01",
        "amount": 400,
    }

    cash_flow_id = 1
    response = client_with_commit_error.put(
        f"/api/v1/cash-flows/{cash_flow_id}",
        json=body,
    )

    result = response.json()
    assert rollback_tracker.called
    assert response.status_code == 500
    assert result["detail"] == "システムエラーが発生しました。"


def test_delete_cash_flow(client: TestClient, db_session: Session) -> None:
    mock_cach_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    cash_flow_id = 1
    response = client.delete(
        f"/api/v1/cash-flows/{cash_flow_id}",
    )

    assert response.status_code == 204


def test_delete_cash_flow_not_found(client: TestClient, db_session: Session) -> None:
    mock_cach_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    cash_flow_id = 2
    response = client.delete(
        f"/api/v1/cash-flows/{cash_flow_id}",
    )

    assert response.status_code == 422
    result = response.json()
    assert result["detail"] == "CashFlow not found!"


def test_delete_cash_flow_error(client_with_commit_error: TestClient,
    rollback_tracker: RollbackTracker,db_session: Session) -> None:
    mock_cach_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    cash_flow_id = 1
    response = client_with_commit_error.delete(
        f"/api/v1/cash-flows/{cash_flow_id}",
    )

    result = response.json()
    assert rollback_tracker.called
    assert response.status_code == 500
    assert result["detail"] == "システムエラーが発生しました。"