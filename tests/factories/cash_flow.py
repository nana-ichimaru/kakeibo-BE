from datetime import datetime

from sqlalchemy.orm import Session

from kakeibo_be.models.db.cash_flow import CashFlow
from kakeibo_be.store.enum.cash_flow_type import CashFlowType


def create_cash_flow(session: Session, **override: dict) -> CashFlow:
    # python ディクショナリ update
    cash_flow_data = {
        "title": "みかん",
        "type": CashFlowType.EXPENSE,
        "recorded_at": datetime(year=2025, month=10, day=1),
        "amount": 200,
    }

    cash_flow_data.update(override)

    cash_flow = CashFlow(**cash_flow_data)

    session.add(cash_flow)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    return cash_flow

