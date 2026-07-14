from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScheduleCreate(BaseModel):
    title: str
    start_datetime: datetime
    end_datetime: datetime | None = None
    memo: str | None = None


class ScheduleUpdate(ScheduleCreate):
    pass


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_datetime: datetime
    end_datetime: datetime | None
    memo: str | None
    created_at: datetime
