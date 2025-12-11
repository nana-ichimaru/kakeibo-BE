from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from kakeibo_be.models.db.base import get_db
from kakeibo_be.models.db.cash_flow import CashFlow
from kakeibo_be.models.request.v1.cash_flow import CreateCashFlowRequest
from kakeibo_be.models.response.v1.cash_flow import CreateCashFlowResponse, GetCashFlowResponseItem
from kakeibo_be.repositories.cash_flow import get_cash_flows_by_moth

router = APIRouter()


@router.get("", response_model=list[GetCashFlowResponseItem])
def get_cash_flows(
    target_month: str, session: Annotated[Session, Depends(get_db)]
) -> list[GetCashFlowResponseItem]:
    month_dt = datetime.strptime(target_month, "%Y-%m")
    a = get_cash_flows_by_moth(session=session, target_month=month_dt)
    result = []
    for item in a:
        b = GetCashFlowResponseItem(
            id=item.id,
            title=item.title,
            type=item.type,
            recorded_at=item.recorded_at,
            amount=item.amount,
        )
        result.append(b)
    return result


@router.post("", response_model=CreateCashFlowResponse)
def create_cash_flow(
    body: CreateCashFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> CreateCashFlowResponse:
    # 保存するための容器を作成
    cash_flow = CashFlow(
        # 設計図をもとに、INSERT対象の1件分（ORMインスタンス）を組み立てている場所
        title=body.title,
        type=body.type,
        recorded_at=body.recorded_at,
        amount=body.amount,
    )
    # セッションに追加（この時点ではまだDBには書き込まれていない）
    session.add(cash_flow)
    # DBに保存。必要ならID採番などが反映される
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    # 保存したデータをレスポンス用に変換して返却
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
