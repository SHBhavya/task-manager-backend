from fastapi import FastAPI, Path, HTTPException, Depends, Query
from sqlalchemy import asc, desc
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

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

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
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

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

    return {"detail": "User deleted"}

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

@app.get("/users/{user_id}/tasks/{task_id}")
def get_user_task(
    user_id: int = Path(..., gt=0),
    task_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    task = db.query(models.Task).filter(models.Task.task_id == task_id, models.Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    return task

@app.put("/users/{user_id}/tasks/{task_id}")
def update_user_task(
                task: schemas.TaskUpdate,
                user_id: int = Path(..., gt=0),
                task_id: int = Path(..., gt=0),
                db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db_task = db.query(models.Task).filter(models.Task.user_id == user_id, models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    return db_task

@app.delete("/users/{user_id}/tasks/{task_id}")
def delete_user_task(
                user_id: int = Path(..., gt=0),
                task_id: int = Path(..., gt=0),
                db: Session = Depends(get_db)
            ):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db_task = db.query(models.Task).filter(models.Task.user_id == user_id, models.Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}

@app.get("/users/{user_id}/tasks")
def get_user_tasks(
    user_id: int,
    status: str = None,
    search: str = None,
    sort: str = "deadline",
    limit: int = 2,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id
    )

    if status:
        tasks = tasks.filter(models.Task.status == status)

    if search:
        tasks = tasks.filter(
            models.Task.title.ilike(f"%{search}%")
        )

    if sort == "deadline":
        tasks = tasks.order_by(models.Task.deadline)

    tasks = tasks.limit(limit).offset(offset).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")

    return tasks