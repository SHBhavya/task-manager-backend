from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# ---------- User Schemas ----------

# Input when creating user
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

# Input when updating a user
class UserUpdate(BaseModel):
    name: Optional[str]=None
    email: Optional[str]=None
    password: Optional[str]=None
    

# Output when returning user
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    is_active: bool

# ---------- Task Schemas ----------

# Create task input
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: TaskStatus = TaskStatus.pending

# Update task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[date] = None


# Task output
class TaskResponse(BaseModel):
    task_id: int
    title: str
    description: Optional[str]
    status: str
    deadline: Optional[date]
    user_id: int

    class Config:
        from_attributes = True
