from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.models.user import User
from app.models.organisation import Organisation


class AiAgent(Base):
    __tablename__ = "ai_agent"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    organisation_id = Column(Integer, ForeignKey("organisation.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    created_by_user = relationship("User", backref="agents")
    organisation = relationship("Organisation", backref="ai_agents")
