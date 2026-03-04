from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from jose import JWTError, jwt
import models, schemas

from core.config import SECRET_KEY, ALGORITHM
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)
from pydantic import BaseModel

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh_token(request: RefreshRequest):
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")

        new_access_token = create_access_token({"sub": user_id})

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.user_id)})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})


    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }