from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import BudgetOut, BudgetUpsert

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
        budget.income_budget = payload.income_budget
        budget.expense_budget = payload.expense_budget
    db.commit()
    db.refresh(budget)
    return budget
