from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.models.user import User
from app.models.organisation import Organisation
from app.models.agents import AiAgent


class CampaignType(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class CampaignStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    paused = "paused"


class Campaign(Base):
    __tablename__ = "campaign"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(CampaignType), nullable=False)
    organisation_id = Column(Integer, ForeignKey("organisation.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organisation = relationship("Organisation", back_populates="campaigns")
    ai_agent = relationship("AiAgent", back_populates="campaigns")
    created_by_user = relationship("User", back_populates="created_campaigns")
