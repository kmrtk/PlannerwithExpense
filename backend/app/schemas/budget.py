from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BudgetUpsert(BaseModel):
    year: int
    month: int
    income_budget: int
    expense_budget: int


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    month: int
    income_budget: int
    expense_budget: int
    created_at: datetime
