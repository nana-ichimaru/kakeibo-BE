from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import RollbackTracker
from tests.factories.cash_flow import create_cash_flow


 # ----------------------------------------
    # pytest.fixture の基本的な使い方
    # ----------------------------------------
    # pytest では、@pytest.fixture で定義された関数（fixture）は、
    # テスト関数の「引数名」に fixture 名を書くことで自動的に利用できる。
    #
    # つまり fixture は、通常の関数のように import して呼び出すのではなく、
    # 「テスト関数の引数に書くだけ」で pytest が自動的に実行し、その戻り値を渡してくれる。
def test_create_cash_flow(client: TestClient) -> None:
    # ----------------------------------------
    # APIに送るリクエストボディ（作成するデータ）
    # ----------------------------------------
    body = {
        "title": "もも",
        "type": "expense",
        "recordedAt": "2025-12-01",
        "amount": 200,
    }

    # ----------------------------------------
    # POST（create）リクエストの書き方
    # ----------------------------------------
    # create（新規作成）のAPIを呼ぶ場合は通常 POST メソッドを使う。
    # そのとき基本的に必要になるのは次の2つ：
    #
    # 1) URL（どのエンドポイントを呼ぶか）
    # 2) body（作成したいデータ）
    #
    # FastAPI/TestClient では json=body と書くことで、
    # body の内容を JSON として送信できる。
    # ----------------------------------------
    response = client.post(
        "/api/v1/cash-flows",  # ① URL（エンドポイント）
        json=body,             # ② JSON形式のbody（作成データ）
    )

    # ----------------------------------------
    # レスポンスの検証（期待通り作成されたか）
    # ----------------------------------------
    assert response.status_code == 200

    # レスポンスボディを JSON（dict）として取得する
    result = response.json()

    # 作成されたデータの id が存在することを確認
    assert result["id"]

    # 送ったデータと同じ内容が返ってきていることを確認
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


    # ----------------------------
    # テストの目的：
    # 「キャッシュフロー更新処理で commit が失敗した場合に、
    #  1) rollback が呼ばれること
    #  2) API が 500 を返すこと
    #  3) エラーメッセージが想定通りであること
    # を確認する
    # ----------------------------
def test_update_cash_flow_error(
    client_with_commit_error: TestClient,
    rollback_tracker: RollbackTracker,
    db_session: Session
) -> None:
    # ----------------------------
    # 事前準備：更新対象のデータをDBに作成する
    # ----------------------------
    # update のテストでは「更新対象のレコードがDBに存在している」必要があるため、
    # テスト開始時に id=1 の cash_flow を作成しておく
    #
    # ※ここでは commit を失敗させたくないため、
    # commit失敗用sessionではなく、通常の db_session を使ってデータを作成する
    mock_cach_flow: dict = {"id": 1}
    create_cash_flow(db_session, **mock_cach_flow)

    # ----------------------------
    # 更新リクエストで送るデータ（PUT の body）を作成する
    # ----------------------------
    # APIに渡すJSON（更新内容）を定義する
    body = {
        "title": "もも",
        "type": "income",
        "recordedAt": "2025-12-01",
        "amount": 400,
    }

    # ----------------------------
    # 更新対象のIDを指定してAPIを叩く
    # ----------------------------
    cash_flow_id = 1

    # client_with_commit_error は、API側で使われる Session の commit が必ず失敗するように
    # dependency override されている TestClient である
    #
    # そのため、APIの更新処理中に session.commit() が呼ばれると、
    # fake_commit が実行され例外が発生し、異常系（commit失敗）を再現できる
    response = client_with_commit_error.put(
        f"/api/v1/cash-flows/{cash_flow_id}",
        json=body,
    )

    # ----------------------------
    # レスポンスの内容を確認する
    # ----------------------------
    # response.json() でレスポンスボディ（JSON）を dict として取得する
    result = response.json()

    # commit失敗時にはAPI側で rollback が呼ばれる想定であり、
    # rollback が呼ばれると fake_rollback により rollback_tracker.called が True になる
    # → rollback が実行されたことをテストで確認する
    assert rollback_tracker.called

    # commit失敗はサーバ内部エラーなので、HTTPステータスは 500 を期待する
    assert response.status_code == 500

    # エラー時のレスポンスの detail が仕様通りのメッセージになっていることを確認する
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