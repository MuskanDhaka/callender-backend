from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import JSONResponse

from app.models.user import User, UserType
from app.models.user_organisation import UserOrganisation
from app.db.session import get_db
from app.dependancy import get_current_user
from app.schemas.user import ShowUser, UserUpdateRole

router = APIRouter(prefix="/editor", tags=["Editor"])


@router.get("/organisation-users", response_model=List[ShowUser])
def get_organisation_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != UserType.editor:
        raise HTTPException(
            status_code=403, detail="Only editors can view organization users"
        )

    org_ids = {uo.org_id for uo in current_user.organisations}

    if not org_ids:
        return []

    users = (
        db.query(User)
        .join(User.organisations)
        .filter(UserOrganisation.org_id.in_(org_ids))
        .all()
    )
    return users


@router.delete("/remove-user/{user_id}", status_code=204)
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserType.editor:
        raise HTTPException(status_code=403, detail="Only editors can remove users")

    current_user_org_ids = {uo.org_id for uo in current_user.organisations}

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user_org_ids = {uo.org_id for uo in target_user.organisations}

    if not current_user_org_ids.intersection(target_user_org_ids):
        raise HTTPException(
            status_code=403, detail="You can only remove users from your organisation"
        )

    db.delete(target_user)
    db.commit()
    return JSONResponse(
        status_code=204, content={"message": "User deleted successfully"}
    )


@router.post("/change-role")
def change_user_role(
    payload: UserUpdateRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserType.editor:
        raise HTTPException(status_code=403, detail="Only editors can change roles")

    current_user_org_ids = {uo.org_id for uo in current_user.organisations}

    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user_org_ids = {uo.org_id for uo in target_user.organisations}

    if not current_user_org_ids.intersection(target_user_org_ids):
        raise HTTPException(
            status_code=403,
            detail="You can only change role of users in your organisation",
        )

    if payload.new_role != UserType.normal:
        raise HTTPException(
            status_code=403,
            detail="Editors can only assign role 'user'",
        )

    target_user.role = payload.new_role
    db.commit()
    db.refresh(target_user)

    return {"message": "User role updated successfully"}
