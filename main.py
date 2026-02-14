from fastapi import FastAPI, Path, HTTPException
from typing import Optional
from database import engine, Base
from pydantic import BaseModel
import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"API is running"}