from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScheduleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    start_datetime: datetime
    end_datetime: datetime | None = None
    memo: str | None = Field(default=None, max_length=1000)
    recurrence_type: Literal["none", "weekly", "monthly"] = "none"
    recurrence_end: date | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("タイトルを入力してください")
        return stripped

    @field_validator("memo")
    @classmethod
    def memo_strip(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @model_validator(mode="after")
    def check_dates(self) -> "ScheduleCreate":
        if self.end_datetime is not None and self.end_datetime < self.start_datetime:
            raise ValueError("終了日時は開始日時以降にしてください")
        if self.recurrence_end is not None and self.recurrence_end < self.start_datetime.date():
            raise ValueError("繰り返し終了日は開始日以降にしてください")
        return self


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
