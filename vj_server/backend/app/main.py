from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import users, images  



UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(images.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


from app.database import Base, engine
from app.models import User

# Создаём таблицы, если их нет
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "FastAPI работает!"}
