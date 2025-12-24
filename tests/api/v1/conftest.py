from collections.abc import Generator

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from kakeibo_be.main import app
from kakeibo_be.models.db.base import get_db


# ----------------------------
# 正常系テスト用の TestClient fixture
# ----------------------------
# FastAPI の Depends(get_db) が返す Session を、fixture で作った db_session に差し替える
# これにより API 側がDBアクセスするときも、テスト用の同じ Session を使うことができる
@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    # get_db の代わりに呼ばれる関数を定義する
    # FastAPI 側で Depends(get_db) している箇所に、この Session が注入される
    def override_get_db() -> Generator[Session]:
        # fixture の db_session をAPI側へ渡す
        yield db_session

    # FastAPI の dependency override 機能を使って、
    # 「通常の get_db」を「override_get_db」に差し替える
    # これにより API の処理はこの db_session を使ってDB操作を行う
    app.dependency_overrides[get_db] = override_get_db

    # FastAPI のアプリに対して HTTP リクエストを送れるテスト用クライアントを作成
    client = TestClient(app)

    try:
        # テスト側へ TestClient を渡す
        yield client

    finally:
        # テストが終わったら override を必ず解除する
        # 解除しないと、他のテストにも override が残ってしまい影響が出るため
        app.dependency_overrides.clear()


# ----------------------------
# commit失敗の異常系テスト用の TestClient fixture
# ----------------------------
# db_session_commit_error（commit を失敗させる Session）を get_db に注入することで、
# API の commit 処理が例外を出す状況を人工的に再現できる
@pytest.fixture
def client_with_commit_error(db_session_commit_error: Session) -> Generator[TestClient]:
    # get_db の代わりに呼ばれる関数を定義する
    # こちらは commit が必ず失敗する Session を返す
    def override_get_db() -> Generator[Session]:
        # commit失敗する Session をAPI側へ渡す
        yield db_session_commit_error

    # FastAPI の get_db を override して、
    # API処理で使われる Session を commit失敗用 Session に置き換える
    app.dependency_overrides[get_db] = override_get_db

    # raise_server_exceptions=False の意味：
    # API側で例外が発生したときに、例外をテスト側へ投げずに
    # 「500レスポンス」として返すようにする設定
    # → 異常系テストで status_code や response body を検証できるようにする
    client = TestClient(app, raise_server_exceptions=False)

    try:
        # テスト側へ TestClient を渡す
        yield client

    finally:
        # テストが終わったら override を必ず解除する
        # 解除しないと他のテストにも影響が残るため
        app.dependency_overrides.clear()