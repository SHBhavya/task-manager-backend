from fastapi import FastAPI, Path, HTTPException, Depends, Query, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal, get_db
import models, schemas
from auth import verify_password, create_access_token, hash_password

router = APIRouter(
    prefix="/users",
    tags=["Tasks"]
)

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

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(user.password)

    new_user = models.User(
        name = user.name, 
        email=user.email,
        password=hashed_password 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get("/{user_id}")
def get_user(
    user_id: int = Path(..., description="The ID you want to get", gt=0),
    db: Session = Depends(get_db)
):  
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.put("/{user_id}")
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

@router.delete("/{user_id}")
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
