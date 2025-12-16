from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from kakeibo_be.exceptions.business_exception import BusinessException
from kakeibo_be.loggers.custom_logger import logger
from kakeibo_be.logic.calculate.calculate_datetime import (
    get_month_start_date,
    get_next_month_start_date,
)
from kakeibo_be.models.db.base import get_db
from kakeibo_be.models.db.cash_flow import CashFlow
from kakeibo_be.models.request.v1.cash_flow import CreateCashFlowRequest, UpdateCashFlowRequest
from kakeibo_be.models.response.v1.cash_flow import (
    CreateCashFlowResponse,
    GetCashFlowResponseItem,
    UpdateCashFlowResponse,
)
from kakeibo_be.repositories.cash_flow import get_cash_flow_by_id, get_cash_flows_by_month

router = APIRouter()


@router.get("", response_model=list[GetCashFlowResponseItem])
def get_cash_flows(
    # http://localhost:8000/api/v1/cash-flows ここから ?target_month=2025-12-12T05%3A43%3A05.419Z
    # target_month: datetime　使いたい関数の引数に設定すると　クエリパラメータ　になる
    target_month: datetime,
    session: Annotated[Session, Depends(get_db)],
) -> list[GetCashFlowResponseItem]:
    # strptime は「文字列を datetime に変換する関数」
    # 2025-12-01 00:00:00

    month_start_date = get_month_start_date(target_month)
    next_month_start_date = get_next_month_start_date(target_month)

    cash_flows = get_cash_flows_by_month(
        session=session,
        month_start_date=month_start_date,
        next_month_start_date=next_month_start_date,
    )
    result = []
    for cash_flow in cash_flows:
        response_item = GetCashFlowResponseItem(
            id=cash_flow.id,
            title=cash_flow.title,
            type=cash_flow.type,
            recorded_at=cash_flow.recorded_at,
            amount=cash_flow.amount,
        )
        # 配列に格納する　表現
        result.append(response_item)
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
        logger.exception("CashFlowの作成に失敗しました。")
        # 意図的にtryの中でキャッチしたエラーを再度発生させてpythonを止める
        raise e

    # 保存したデータをレスポンス用に変換して返却
    return CreateCashFlowResponse(
        id=cash_flow.id,
        title=cash_flow.title,
        type=cash_flow.type,
        recorded_at=cash_flow.recorded_at,
        amount=cash_flow.amount,
    )


@router.put("/{cash_flow_id}", response_model=UpdateCashFlowResponse)
def update_cash_flow(
    cash_flow_id: int, body: UpdateCashFlowRequest, session: Annotated[Session, Depends(get_db)]
) -> UpdateCashFlowResponse:
    original_cash_flow = get_cash_flow_by_id(session=session, cash_flow_id=cash_flow_id)

    if original_cash_flow is None:
        logger.info(f"該当する更新対象のCashFlow IDが見つかりません。id = {cash_flow_id}")
        raise BusinessException(message="CashFlow not found!")
    original_cash_flow.title = body.title
    original_cash_flow.type = body.type
    original_cash_flow.recorded_at = body.recorded_at
    original_cash_flow.amount = body.amount

    session.add(original_cash_flow)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception("CashFlowの更新に失敗しました。")
        # 意図的にtryの中でキャッチしたエラーを再度発生させてpythonを止める
        raise e

    return UpdateCashFlowResponse(
        id=original_cash_flow.id,
        title=original_cash_flow.title,
        type=original_cash_flow.type,
        recorded_at=original_cash_flow.recorded_at,
        amount=original_cash_flow.amount,
    )


# 対象のidを特定（パスパラメータ）
# レスポンスは無しなので　None
@router.delete("/{cash_flow_id}", response_model=None, status_code=204)
def delete_cash_flow(cash_flow_id: int, session: Annotated[Session, Depends(get_db)]) -> None:
    # 対象のidのCashFlowを取得
    cash_flow = get_cash_flow_by_id(session=session, cash_flow_id=cash_flow_id)
    # 存在しなければエラーを返す
    if cash_flow is None:
        logger.info("該当する削除対象のCashFlow IDが見つかりません。")
        raise BusinessException(message="CashFlow not found!")
    # 存在すれば削除
    session.delete(cash_flow)

    # コミット処理
    try:
        session.commit()
    # エラーがExceptionを継承していればキャッチする
    except Exception as e:
        session.rollback()
        logger.exception("CashFlowの削除に失敗しました。")
        # ロールバックしたあと、キャッチした例外を再送出して処理を中断する
        raise e
