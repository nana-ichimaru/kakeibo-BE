from datetime import datetime
from zoneinfo import ZoneInfo


def get_now() -> datetime:
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def get_month_start_date(target_month: datetime) -> datetime:
    return target_month.replace(
        tzinfo=ZoneInfo("Asia/Tokyo"), day=1, hour=0, minute=0, second=0, microsecond=0
    )


def get_next_month_start_date(target_month: datetime) -> datetime:
    if target_month.month == 12:
        # 12月だったら → 翌年の1月にする（year+1, month=1）
        return target_month.replace(
            tzinfo=ZoneInfo("Asia/Tokyo"),
            year=target_month.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
    else:
        # それ以外は → 単純に月を+1する
        return target_month.replace(
            tzinfo=ZoneInfo("Asia/Tokyo"),
            month=target_month.month + 1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
