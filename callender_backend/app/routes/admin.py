from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, ShowUser, SetPassword
from app.models.user import User, UserType
from app.db.session import get_db
from app.auth.hashing import hash_password
from app.dependancy import get_current_user
import secrets
from app.schemas.user import ShowUser, UserUpdateRole
from app.models.user_organisation import UserOrganisation
from typing import List
from app.schemas.organisation import ShowOrganisation, CreateOrganisation
from app.models.organisation import Organisation
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/create-user", response_model=ShowUser)
def create_user_as_admin(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserType.admin:
        raise HTTPException(status_code=403, detail="Only admins can create users")

    otp_token = secrets.token_urlsafe(32)

    new_user = User(
        username=request.username,
        email=request.email,
        role=request.role,
        otp_token=otp_token,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"Set password link: /admin/set-password?token={otp_token}")
    return new_user


@router.post("/set-password")
def set_user_password(payload: SetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.otp_token == payload.token).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid token")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Password already set")

    user.password = hash_password(payload.password)
    user.otp_token = None
    user.is_verified = True
    db.commit()
    return {"message": "Password set successfully"}


@router.get("/organisation-users", response_model=List[ShowUser])
def get_organisation_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role != UserType.admin:
        raise HTTPException(
            status_code=403, detail="Only admins can view organization users"
        )
    org_ids = [org.org_id for org in current_user.organisations]

    if not org_ids:
        return []

    users = (
        db.query(User)
        .join(User.organisations)
        .filter(UserOrganisation.org_id in (org_ids))
        .all
    )
    return users


@router.post("/change-role")
def change_user_role(
    payload: UserUpdateRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserType.admin:
        raise HTTPException(status_code=403, detail="Only admin can change user roles")
    admin_org_ids = {uo.org_id for uo in current_user.organisations}

    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user_org_ids = {uo.org_id for uo in target_user.organisations}

    if not admin_org_ids.intersection(target_user_org_ids):
        raise HTTPException(
            status_code=403,
            detail="You can only change role of users in your organisation ",
        )
    target_user.role = payload.new_role
    db.commit()
    db.refresh(User)
    return {"message": "user role updated successfully"}


@router.post("/create-organisation", response_model=ShowOrganisation)
def create_organisation(
    payload: CreateOrganisation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserType.admin:
        raise HTTPException(
            status_code=403, detail="Only admins can create organisation"
        )

    existing_org = (
        db.query(Organisation).filter(Organisation.name == payload.name).first()
    )
    if existing_org:
        raise HTTPException(
            status_code=400, detail="Organisation with this name already exist"
        )

    org = Organisation(name=payload.name, type=payload.type)
    db.add(org)
    db.commit()
    db.refresh(org)

    membership = UserOrganisation(user_id=current_user.id, org_id=org.id)
    db.add(membership)
    db.commit()

    return org


@router.delete("/remove-user/{user_id}", status_code=204)
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserType.admin:
        raise HTTPException(status_code=403, detail="only admins can remove users")

    admin_org_ids = {uo.org_id for uo in current_user.organisations}

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user_org_ids = {uo.org_id for uo in target_user.organisations}

    if not admin_org_ids.intersection(target_user_org_ids):
        raise HTTPException(
            status_code=403, detail="you can only remove users from your organisation"
        )
    db.delete(target_user)
    db.commit()
    return JSONResponse(
        status_code=204, content={"message": "User deleted successfully"}
    )
