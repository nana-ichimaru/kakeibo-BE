from datetime import datetime

from pydantic import Field

from kakeibo_be.models.request.v1.base import BaseRequest
from kakeibo_be.store.enum.cash_flow_type import CashFlowType


class CreateCashFlowRequest(BaseRequest):
    title: str
    type: CashFlowType
    recorded_at: datetime
    amount: int = Field(gt=0)

class UpdateCashFlowRequest(BaseRequest):
    title: str
    type: CashFlowType
    recorded_at: datetime
    amount: int 
