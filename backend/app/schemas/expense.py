from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    type: Literal["income", "expense"] = "expense"
    amount: int
    date: date
    category: str
    memo: str | None = None


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
