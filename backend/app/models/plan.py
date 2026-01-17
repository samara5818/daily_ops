from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, JSON

from app.db.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    now_iso = Column(String(25), nullable=False)

    plan_json = Column(JSON, nullable=True)
    actions_json = Column(JSON, nullable=True)
    warnings_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
