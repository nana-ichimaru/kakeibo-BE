from datetime import date

from sqlalchemy.orm import Session

from kakeibo_be.repositories.cash_flow import get_cash_flow_by_id
from kakeibo_be.store.enum.cash_flow_type import CashFlowType
from tests.factories.cash_flow import create_cash_flow


# db_sessionは、@pytest.fixture conftestに記述しているから使える
def test_get_cash_flow_by_id(db_session: Session) -> None:
    for i in range(1, 5):
        mock_cach_flow = {
            "id": i,
            "title": f"もも_{i}",
            "recorded_at": date(year=2025, month=10, day=i),
            "amount": 100 * i,
        }
        create_cash_flow(db_session, **mock_cach_flow)

    target_id = 2
    result = get_cash_flow_by_id(session=db_session, cash_flow_id=target_id)

    assert result
    assert result.id == target_id
    assert result.title == f"もも_{target_id}"
    assert result.type == CashFlowType.EXPENSE
    assert result.recorded_at == date(year=2025, month=10, day=target_id)
    assert result.amount == 100 * target_id


def test_get_cash_flow_by_id_without_data(db_session: Session) -> None:
    mock_cash_flow:dict = {"id": 1}
    create_cash_flow(db_session, **mock_cash_flow)

    result = get_cash_flow_by_id(session=db_session, cash_flow_id=2)

    assert not result
