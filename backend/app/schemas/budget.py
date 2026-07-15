from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BudgetUpsert(BaseModel):
    year: int
    month: int
    savings_target: int


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    month: int
    savings_target: int
    created_at: datetime


class MonthlyBudgetSummary(BaseModel):
    month: int
    savings_target: int
    actual_income: int
    actual_expense: int


class AllTimeSummary(BaseModel):
    start_year: int | None
    end_year: int | None
    total_savings: int
