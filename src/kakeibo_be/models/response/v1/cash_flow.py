from datetime import datetime

from pydantic import BaseModel

from kakeibo_be.store.enum.cash_flow_type import CashFlowType


class CreateCashFlowResponse(BaseModel):
    id: int
    title: str
    type: CashFlowType
    recorded_at: datetime
    amount: int