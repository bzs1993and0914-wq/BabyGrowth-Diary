"""记录日期校验：禁止「今天」之后的日期。"""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException


def assert_record_date_not_after_today(date_str: str) -> None:
    """若 date_str（YYYY-MM-DD）晚于服务端本地日历的「今天」，抛出 422。"""
    try:
        parsed = date.fromisoformat(date_str)
    except ValueError as e:
        raise HTTPException(status_code=422, detail="日期格式无效") from e
    if parsed > date.today():
        raise HTTPException(status_code=422, detail="记录日期不能晚于今天")
