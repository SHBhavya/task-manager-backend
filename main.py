from fastapi import FastAPI, Path, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models, schemas

#DB Connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"API is running"}

@app.post("/users")
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

@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., description="The ID you want to get", gt=0),
    db: Session = Depends(get_db)
):  
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@app.put("/users/{user_id}")
def update_user(
                user: schemas.UserUpdate,
                user_id: int = Path(..., gt=0),
                db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.name:
        db_user.name = user.name
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.password = user.password

    db.commit()
    db.refresh(db_user)

    return db_user

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()

    return user

@app.post("/users/{user_id}/tasks")
def create_task(
    task: schemas.TaskCreate,
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    new_task = models.Task(**task.model_dump(), user_id=user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@app.get("/users/{user_id}/tasks")
def get_user_tasks(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    tasks = db.query(models.Task).filter(models.Task.user_id == user_id).all()
    return tasks