from datetime import datetime

from pydantic import BaseModel, Field

from kakeibo_be.store.enum.cash_flow_type import CashFlowType


class CreateCashFlowRequest(BaseModel):
    title: str
    type: CashFlowType
    recorded_at: datetime
    amount: int = Field(gt=0)
