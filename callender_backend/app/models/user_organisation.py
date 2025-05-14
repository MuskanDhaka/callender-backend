from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from app.db.base import Base
from app.models.user import User
from app.models.organisation import Organisation

from sqlalchemy.orm import relationship


class UserOrganisation(Base):
    __tablename__ = "user_organisation"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organisation.id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("user_id", "org_id"),)

    user = relationship("User", back_populates="organisations")
    organisation = relationship("Organisation", back_populates="users")
