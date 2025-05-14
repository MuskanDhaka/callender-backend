from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Campaign(Base):
    __tablename__ = "campaign"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    org_id = Column(Integer, ForeignKey("organisation.id"), nullable=False)
    ai_agent_id = Column(Integer, ForeignKey("ai_agent.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
