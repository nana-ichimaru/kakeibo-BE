from collections.abc import Generator
from pathlib import Path

import pytest

from alembic import command
from alembic.config import Config

from kakeibo_be.core.database import get_database_url


# テストの開始1回目に自動でapply_migrations()が実行される設定
@pytest.fixture(scope="session",autouse=True)
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
