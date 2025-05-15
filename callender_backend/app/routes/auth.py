from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import Login
from app.db.session import get_db
from app.models.user import User
from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token

router = APIRouter(tags=["Authentication"])


@router.post("/auth/login")
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = request.username  # <- This will actually be the email
    password = request.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
