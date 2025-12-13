from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session

from kakeibo_be.models.db.cash_flow import CashFlow


def get_cash_flows_by_month(
    session: Session, month_start_date: datetime, next_month_start_date: datetime
) -> list[CashFlow]:
    stmt = (
        # CashFlow テーブル（モデル）を対象にした SELECT クエリを作成
        select(CashFlow)
        # recorded_at が start_date 以上（＝月初以降）を指定
        .where(CashFlow.recorded_at >= month_start_date)
        # recorded_at が end_date 未満（＝翌月の月初より前）を指定
        .where(CashFlow.recorded_at < next_month_start_date)
    )
    # 型は Result（SQLAlchemy の「結果セット」を表すオブジェクト）。
    # SQLAlchemy で組み立てた stmt（SQL文の設計図）を、実際にデータベースに送って実行する
    result: Result = session.execute(stmt)

    # scalars() がなかったら → Row のリストが返ってくる
    # result.scalars() で 1行の中の「一番左のカラム（= CashFlow オブジェクト）」だけを取り出してくれる
    return list(result.scalars())

def get_cash_flow_by_id(session: Session, cash_flow_id: int) -> CashFlow | None:
    result: Result = session.execute(
        select(CashFlow).where(CashFlow.id == cash_flow_id)
    )

    # scalars()で結果をオブジェクトとして取得し、first()で最初の1件を返す
    # 対応するTaskが存在しない場合は None を返す
    return result.scalars().first()


    
