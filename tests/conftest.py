from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import Connection, create_engine
from sqlalchemy.orm import Session, sessionmaker

from kakeibo_be.core.database import get_database_url

# 環境変数はここにあることを伝える。
load_dotenv(".env.test.unit")


# テストの開始1回目に自動でapply_migrations()が実行される設定
@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> Generator[None]:
    """pytest開始時にテストDBへAlembicマイグレーションを適用する"""

    # プロジェクトルートを基準に alembic.ini を取得
    # __file__このファイル
    # .resolve()解決してください。ファイルの場所の把握をしてください
    # このファイルがあるフォルダの親.parents[1]
    project_root = Path(__file__).resolve().parents[1]
    # alembic.ini があるディレクトリ
    alembic_dir = project_root / "src" / "kakeibo_be"
    # alembic.iniのあるファイルのパスを指定
    alembic_ini_path = alembic_dir / "alembic.ini"

    # alembic.ini を絶対パスで読み込む
    alembic_cfg = Config(str(alembic_ini_path))

    # 動的に sqlalchemy.url をテスト用に書き換える
    db_url = get_database_url()
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # 最新の head までアップグレード
    command.upgrade(alembic_cfg, "head")

    yield


@pytest.fixture
def db_connection() -> Generator[Connection]:
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    connection = engine.connect()
    # 調べる
    transaction = connection.begin()
    try:
        yield connection
    finally:
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def db_session(db_connection:Connection) -> Generator[Session]:
    testing_session = sessionmaker(bind=db_connection)

    test_db = testing_session()
    try:
        yield test_db
    finally:
        test_db.close()


# transactionがなかった場合、rollback()をしなかった場合、transaction.rollback()をコメントアウトした場合の挙動を見てみる


# 設計図
@dataclass
class RollbackTracker:
    called: bool = False


# インスタンス
@pytest.fixture
def rollback_tracker() -> RollbackTracker:
    return RollbackTracker()


@pytest.fixture
# 処理の結果の変更
def db_session_commit_error(
    db_connection:Connection, rollback_tracker: RollbackTracker, monkeypatch: pytest.MonkeyPatch
) -> Generator[Session]:
    testing_session = sessionmaker(bind=db_connection)

    test_db_session = testing_session()
    original_rollback = test_db_session.rollback


    # attr アトラクターの略　調べる
    # monkeypatch.setattr引数は三つで、
    def fake_commit() -> None:
        raise Exception("commitに失敗しました。")

    def fake_rollback() -> None:
        rollback_tracker.called = True
        original_rollback()

    monkeypatch.setattr(test_db_session, "commit", fake_commit)
    monkeypatch.setattr(test_db_session, "rollback", fake_rollback)
    try:
        yield test_db_session
    finally:
        test_db_session.close()
    
    
