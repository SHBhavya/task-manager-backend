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
    return {"message":"User created!"}