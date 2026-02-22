from fastapi import FastAPI
from database import engine, Base, SessionLocal
from routers import tasks, users

app = FastAPI()
app.include_router(users.router)
app.include_router(tasks.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "API is running"}
