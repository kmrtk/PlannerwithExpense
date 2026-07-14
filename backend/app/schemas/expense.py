from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    amount: int
    date: date
    category: str
    memo: str | None = None


class ExpenseUpdate(ExpenseCreate):
    pass


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: int
    date: date
    category: str
    memo: str | None
    created_at: datetime
