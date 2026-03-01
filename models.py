from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Boolean, Enum
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enums import TaskStatus

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    tasks = relationship("Task", back_populates="user", cascade="all, delete")

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    deadline = Column(Date)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    user = relationship("User", back_populates="tasks")