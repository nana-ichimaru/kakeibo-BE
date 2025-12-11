from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session

from kakeibo_be.models.db.cash_flow import CashFlow


def get_cash_flows_by_moth(session: Session, target_month: datetime) -> list[CashFlow]:
    # 月初
    start_date = target_month.replace(day=1)

    # 翌月の月初 = 範囲の終わり
    if start_date.month == 12:
        end_date = start_date.replace(year=start_date.year + 1, month=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1)

    stmt = (
        select(CashFlow)
        .where(CashFlow.recorded_at >= start_date)
        .where(CashFlow.recorded_at < end_date)
    )

    result: Result = session.execute(stmt)
    return list(result.scalars().all())
