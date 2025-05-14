from pydantic import BaseModel
from enum import Enum as PyEnum
from datetime import datetime
from typing import Optional


class OrganisationType(str, PyEnum):
    lawyer = "lawyer"
    clinic = "clinic"
    default = "default"


class CreateOrganisation(BaseModel):
    name: str
    type: OrganisationType


class ShowOrganisation(BaseModel):
    id: int
    name: str
    type: OrganisationType
    created_at: datetime

    class Config:
        from_attributes = True
