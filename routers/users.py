from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from core.security import verify_password, create_access_token, hash_password, get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user)
):
    return current_user



@router.put("/me", response_model=schemas.UserResponse)
def update_user(
    user: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    db_user = db.query(models.User).filter(
        models.User.user_id == current_user.user_id
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    update_data = user.model_dump(exclude_unset=True)

    # If password is being updated → hash it
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/me")
def delete_user(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.user_id == current_user.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.delete(user)
    db.commit()

    return {"detail": "User deleted"}