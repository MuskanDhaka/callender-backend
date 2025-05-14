from sqlalchemy import Column, Integer, String, DateTime, Enum, func, Boolean
from app.db.base import Base
import enum
from sqlalchemy.orm import relationship


class UserType(str, enum.Enum):
    normal = "normal"
    admin = "admin"
    editor = "editor"


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, index=True, nullable=False)
    role = Column(Enum(UserType), nullable=False, default=UserType.admin)
    otp_token = Column(String, nullable=True, unique=True)  # one-time token
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organisations = relationship("UserOrganisation", back_populates="user")
