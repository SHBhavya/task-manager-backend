from fastapi import FastAPI, Path, HTTPException, Depends, Query, APIRouter
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal, get_db
import models, schemas

router = APIRouter()

@router.get("/")
def home():
    return {"message":"API is running"}

@router.post("/users")
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    new_user = models.User(
        name = user.name, 
        email=user.email,
        password=user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., description="The ID you want to get", gt=0),
    db: Session = Depends(get_db)
):  
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.put("/users/{user_id}")
def update_user(
                user: schemas.UserUpdate,
                user_id: int = Path(..., gt=0),
                db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()

    return {"detail": "User deleted"}
