from datetime import datetime

from sqlalchemy import Date, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from kakeibo_be.logic.calculate.calculate_datetime import get_now
from kakeibo_be.models.db.base import Base
from kakeibo_be.store.enum.cash_flow_type import CashFlowType


class CashFlow(Base):
    __tablename__ = "cash_flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    type: Mapped[CashFlowType] = mapped_column(Enum(CashFlowType), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=get_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=get_now, onupdate=get_now
    )
