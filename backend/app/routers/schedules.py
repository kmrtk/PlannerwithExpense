from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


def _month_range(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def _get_owned_schedule(schedule_id: int, db: Session, current_user: User) -> Schedule:
    schedule = (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.user_id == current_user.id)
        .first()
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="予定が見つかりません")
    return schedule


@router.get("", response_model=list[ScheduleOut])
def list_schedules(
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Schedule).filter(Schedule.user_id == current_user.id)
    if year is not None and month is not None:
        start, end = _month_range(year, month)
        query = query.filter(Schedule.start_datetime >= start, Schedule.start_datetime < end)
    return query.order_by(Schedule.start_datetime).all()


@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = Schedule(**payload.model_dump(), user_id=current_user.id)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleOut)
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = _get_owned_schedule(schedule_id, db, current_user)
    for key, value in payload.model_dump().items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = _get_owned_schedule(schedule_id, db, current_user)
    db.delete(schedule)
    db.commit()
