from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ScheduleCreate(BaseModel):
    title: str
    start_datetime: datetime
    end_datetime: datetime | None = None
    memo: str | None = None
    recurrence_type: Literal["none", "weekly", "monthly"] = "none"
    recurrence_end: date | None = None


class ScheduleUpdate(ScheduleCreate):
    pass


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_datetime: datetime
    end_datetime: datetime | None
    memo: str | None
    recurrence_type: Literal["none", "weekly", "monthly"]
    recurrence_end: date | None
    created_at: datetime
