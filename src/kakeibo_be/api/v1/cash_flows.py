from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from kakeibo_be.models.db.base import get_db
from kakeibo_be.models.db.cash_flow import CashFlow
from kakeibo_be.models.request.v1.cash_flow import CreateCashFlowRequest
from kakeibo_be.models.response.v1.cash_flow import CreateCashFlowResponse

router = APIRouter()


@router.get("")
def get_cash_flows() -> dict:
    return {"status": "ok"}


@router.post("", response_model=CreateCashFlowResponse)
def create_cash_flow(
    body: CreateCashFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> CreateCashFlowResponse:
    # 保存するための容器を作成
    cash_flow = CashFlow(
        title=body.title,
        type=body.type,
        recorded_at=body.recorded_at,
        amount=body.amount,
    )
    session.add(cash_flow)
    session.commit()

    return CreateCashFlowResponse(
        id=cash_flow.id,
        title=cash_flow.title,
        type=cash_flow.type,
        recorded_at=cash_flow.recorded_at,
        amount=cash_flow.amount,
    )


@router.put("")
def update_cash_flow() -> dict:
    return {"status": "ok"}


@router.delete("")
def delete_cash_flow() -> dict:
    return {"status": "ok"}
