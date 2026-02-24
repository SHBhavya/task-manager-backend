from fastapi import FastAPI, Path, HTTPException, Depends, Query, APIRouter
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal, get_db
import models, schemas
from auth import get_current_user

router = APIRouter(
    prefix="/users/{user_id}/tasks",
    tags=["Tasks"]
)


@router.post("/")
def create_task(
    task: schemas.TaskCreate,
    user_id: int = Path(..., gt=0),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🔐 Ensure logged-in user matches path user_id
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_task = models.Task(
        title=task.title,
        description=task.description,
        user_id=current_user.user_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/{task_id}")
def get_user_task(
    user_id: int = Path(..., gt=0),
    task_id: int = Path(..., gt=0),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🔐 Authorization check
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = db.query(models.Task).filter(
        models.Task.task_id == task_id,
        models.Task.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


@router.put("/{task_id}")
def update_user_task(
    task: schemas.TaskUpdate,
    user_id: int = Path(..., gt=0),
    task_id: int = Path(..., gt=0),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🔐 Authorization check
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_task = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.task_id == task_id
    ).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found.")

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    return db_task


@router.delete("/{task_id}")
def delete_user_task(
    user_id: int = Path(..., gt=0),
    task_id: int = Path(..., gt=0),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🔐 Authorization check
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_task = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.task_id == task_id
    ).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found.")

    db.delete(db_task)
    db.commit()

    return {"detail": "Task deleted"}


@router.get("/")
def get_user_tasks(
    user_id: int = Path(..., gt=0),
    status: str = None,
    search: str = None,
    sort: str = "deadline",
    limit: int = 2,
    offset: int = 0,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🔐 Authorization check
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    tasks = db.query(models.Task).filter(
        models.Task.user_id == user_id
    )

    if status:
        tasks = tasks.filter(models.Task.status == status)

    if search:
        tasks = tasks.filter(
            or_(
                models.Task.title.ilike(f"%{search}%"),
                models.Task.description.ilike(f"%{search}%")
            )
        )

    total = tasks.count()

    if sort == "deadline":
        tasks = tasks.order_by(models.Task.deadline)

    tasks = tasks.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": tasks
    }