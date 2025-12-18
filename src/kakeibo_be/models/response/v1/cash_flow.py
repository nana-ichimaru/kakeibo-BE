from datetime import date

from kakeibo_be.models.response.v1.base import BaseResponse
from kakeibo_be.store.enum.cash_flow_type import CashFlowType


class CreateCashFlowResponse(BaseResponse):
    id: int
    title: str
    type: CashFlowType
    recorded_at: date
    amount: int


class GetCashFlowResponseItem(BaseResponse):
    id: int
    title: str
    type: CashFlowType
    recorded_at: date
    amount: int


class UpdateCashFlowResponse(BaseResponse):
    id: int
    title: str
    type: CashFlowType
    recorded_at: date
    amount: int
