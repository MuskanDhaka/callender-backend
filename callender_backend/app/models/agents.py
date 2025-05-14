from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class AiAgent(Base):
    __tablename__ = "ai_agent"  # ✅ FIXED: no hyphen
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_by = Column(Integer, ForeignKey("user.id"))
    organisation_id = Column(Integer, ForeignKey("organisation.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
