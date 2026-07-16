from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

MAX_SAVINGS_TARGET = 100_000_000


class BudgetUpsert(BaseModel):
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    savings_target: int = Field(ge=0, le=MAX_SAVINGS_TARGET)


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
