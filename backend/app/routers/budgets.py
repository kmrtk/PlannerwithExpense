from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.budget import Budget
from app.models.expense import Expense
from app.models.user import User
from app.schemas.budget import AllTimeSummary, BudgetOut, BudgetUpsert, MonthlyBudgetSummary

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("", response_model=BudgetOut | None)
def get_budget(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id, Budget.year == year, Budget.month == month)
        .first()
    )


@router.get("/yearly", response_model=list[MonthlyBudgetSummary])
def get_yearly_summary(
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id, Budget.year == year).all()
    savings_target_by_month = {b.month: b.savings_target for b in budgets}

    rows = (
        db.query(
            func.month(Expense.date).label("month"),
            func.sum(case((Expense.type == "income", Expense.amount), else_=0)).label("income"),
            func.sum(case((Expense.type != "income", Expense.amount), else_=0)).label("expense"),
        )
        .filter(
            Expense.user_id == current_user.id,
            Expense.date >= date(year, 1, 1),
            Expense.date < date(year + 1, 1, 1),
        )
        .group_by(func.month(Expense.date))
        .all()
    )
    income_by_month = {r.month: r.income for r in rows}
    expense_by_month = {r.month: r.expense for r in rows}

    return [
        MonthlyBudgetSummary(
            month=month,
            savings_target=savings_target_by_month.get(month, 0),
            actual_income=income_by_month.get(month, 0),
            actual_expense=expense_by_month.get(month, 0),
        )
        for month in range(1, 13)
    ]


@router.get("/all-time-summary", response_model=AllTimeSummary)
def get_all_time_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = (
        db.query(
            func.min(func.year(Expense.date)).label("start_year"),
            func.max(func.year(Expense.date)).label("end_year"),
            func.sum(case((Expense.type == "income", Expense.amount), else_=0)).label("total_income"),
            func.sum(case((Expense.type != "income", Expense.amount), else_=0)).label("total_expense"),
        )
        .filter(Expense.user_id == current_user.id)
        .one()
    )
    if result.start_year is None:
        return AllTimeSummary(start_year=None, end_year=None, total_savings=0)

    return AllTimeSummary(
        start_year=result.start_year,
        end_year=result.end_year,
        total_savings=(result.total_income or 0) - (result.total_expense or 0),
    )


@router.put("", response_model=BudgetOut)
def upsert_budget(
    payload: BudgetUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.year == payload.year,
            Budget.month == payload.month,
        )
        .first()
    )
    if budget is None:
        budget = Budget(user_id=current_user.id, **payload.model_dump())
        db.add(budget)
    else:
        budget.savings_target = payload.savings_target
    db.commit()
    db.refresh(budget)
    return budget
