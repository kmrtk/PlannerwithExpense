from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Expense(Base):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(String(10), nullable=False, default="expense", server_default="expense")
    amount = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(255), nullable=False)
    memo = Column(String(1000), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="expenses")
