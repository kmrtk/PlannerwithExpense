from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_AMOUNT = 100_000_000


class ExpenseCreate(BaseModel):
    type: Literal["income", "expense"] = "expense"
    amount: int = Field(gt=0, le=MAX_AMOUNT)
    date: date
    category: str = Field(min_length=1, max_length=255)
    memo: str | None = Field(default=None, max_length=1000)

    @field_validator("category")
    @classmethod
    def category_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("カテゴリを入力してください")
        return stripped

    @field_validator("memo")
    @classmethod
    def memo_strip(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class ExpenseUpdate(ExpenseCreate):
    pass


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: Literal["income", "expense"]
    amount: int
    date: date
    category: str
    memo: str | None
    created_at: datetime
