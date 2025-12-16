from datetime import datetime
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta


def get_now() -> datetime:
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def get_month_start_date(target_month: datetime) -> datetime:
    return target_month.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=ZoneInfo("Asia/Tokyo"),
    )


def get_next_month_start_date(target_month: datetime) -> datetime:
    return target_month.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=ZoneInfo("Asia/Tokyo"),
    ) + relativedelta(months=1)
