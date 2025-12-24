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
    # テスト用のDB接続URLを取得する
    database_url = get_database_url()
    # SQLAlchemyのEngineを作成する（DB接続を管理するための入り口）
    # echo=False なので SQLログは出力しない（必要なら True にするとSQLが表示される）
    engine = create_engine(database_url, echo=False)
    # Engine から DB への接続（Connection）を取得する
    # この connection を正常系/異常系テストで共通利用することで、
    # 「テストデータ作成」と「API処理」で別connectionになってデータが見えない、などの問題を防ぐ
    connection = engine.connect()
    # ここでトランザクションを開始する
    # この connection を使って行われるDB操作は、このトランザクションの中に入る
    # テストが終わったら rollback することで、DBを元の状態に戻し、テスト間の影響をなくす
    transaction = connection.begin()
    try:
        # テスト側に connection を渡す
        # テストが実行されている間、この connection と transaction は維持される
        yield connection
    finally:
        # テスト終了後の後始末
        # transaction がまだ有効（active）な場合のみ rollback を実行する
        # ※ commit や rollback 済みで transaction が終了している場合は rollback しない
        if transaction.is_active:
            transaction.rollback()

        # 最後に connection を必ず閉じる（リソース解放）
        connection.close()

@pytest.fixture
def db_session(db_connection: Connection) -> Generator[Session]:
    # db_connection fixture で作成した Connection を使って Session を作るための設定を作成する
    # bind=db_connection にすることで、テストデータ作成とAPI処理で同じ connection を共有できる
    # （別connectionになると、transactionが分かれてデータが見えない等の問題が起きる）
    testing_session = sessionmaker(bind=db_connection)
    # 上で作った設定（sessionmaker）から Session インスタンスを作成する
    # この Session をテストで使い回す
    test_db = testing_session()
    try:
        # テスト側に Session を渡す
        # テストが実行されている間、この Session を使ってDB操作を行う
        yield test_db
    finally:
        # テスト終了後に Session を閉じてリソース解放する
        # ※ rollback/transaction管理自体は db_connection 側の fixture で行われる
        test_db.close()


# transactionがなかった場合、rollback()をしなかった場合、transaction.rollback()をコメントアウトした場合の挙動を見てみる



# ----------------------------
# RollbackTracker（設計図）
# ----------------------------
# rollback が呼ばれたかどうかを「テストで判定できる形」にするためのクラス
# called が True になれば「rollback が実行された」と判断できる
# dataclass にすることで、シンプルに状態（called）を持つクラスを作れる
@dataclass
class RollbackTracker:
    # rollback が呼ばれたかどうかを表すフラグ
    # 初期値は False（まだ rollback は呼ばれていない）
    called: bool = False


# ----------------------------
# RollbackTracker（インスタンス生成）
# ----------------------------
# テストごとに新しい RollbackTracker を生成して返す fixture
# これによりテスト間で状態が混ざらない（毎回 called=False から始まる）
@pytest.fixture
def rollback_tracker() -> RollbackTracker:
    return RollbackTracker()


# ----------------------------
# commit を意図的に失敗させる Session を作る fixture
# ----------------------------
# 正常系の Session と別に、この fixture で作る Session では commit() を差し替えて
# commit 失敗の異常系を再現できるようにする
@pytest.fixture
def db_session_commit_error(
    db_connection: Connection,
    rollback_tracker: RollbackTracker,
    monkeypatch: pytest.MonkeyPatch
) -> Generator[Session]:
    # db_connection fixture で作成した Connection を bind して Session を作る設定を作成する
    # bind を統一することで、テストデータ作成とAPI処理で同じ connection を利用できる
    testing_session = sessionmaker(bind=db_connection)

    # 上で作った設定から Session インスタンスを作成する
    test_db_session = testing_session()

    # rollback を差し替える前に、本来の rollback メソッドを退避しておく
    # fake_rollback の中で、本来の rollback を呼びたいので保存している
    original_rollback = test_db_session.rollback

    # ----------------------------
    # commit / rollback の動きをテスト用に差し替える関数を用意する
    # ----------------------------

    # commit を呼ぶと必ず例外になる関数
    # → commit失敗の異常系を人工的に発生させるために使う
    def fake_commit() -> None:
        raise Exception("commitに失敗しました。")

    # rollback を呼ぶと、
    # 1) rollback_tracker.called を True にして「rollbackが呼ばれた」ことを記録
    # 2) その後、本来の rollback を実行して実際にDB状態も戻す
    def fake_rollback() -> None:
        # rollback が呼ばれたことを記録（テストで assert rollback_tracker.called ができる）
        rollback_tracker.called = True

        # 本来の rollback を実行（DB状態を正しく戻す）
        original_rollback()

    # ----------------------------
    # monkeypatch による差し替え
    # ----------------------------
    # monkeypatch.setattr は「指定したオブジェクトの属性（メソッド等）をテスト中だけ差し替える」仕組み
    # 第1引数：差し替え対象のオブジェクト（test_db_session）
    # 第2引数：差し替える属性名（"commit" / "rollback"）
    # 第3引数：置き換える関数（fake_commit / fake_rollback）
    #
    # これにより、
    # - test_db_session.commit() を呼ぶと fake_commit が実行される（＝必ず例外）
    # - test_db_session.rollback() を呼ぶと fake_rollback が実行される（＝呼ばれた記録が残る）
    monkeypatch.setattr(test_db_session, "commit", fake_commit)
    monkeypatch.setattr(test_db_session, "rollback", fake_rollback)

    try:
        # commit が失敗する特殊な Session をテスト側へ渡す
        yield test_db_session

    finally:
        # テスト終了後に Session を閉じてリソース解放
        test_db_session.close()