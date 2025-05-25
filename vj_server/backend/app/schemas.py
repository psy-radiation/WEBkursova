from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(UserCreate):
    pass

class UserBase(BaseModel):
    username: str
    background: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ImageUpload(BaseModel):
    title: str

class ImageOut(BaseModel):
    id: int
    title: str
    filename: str
    upload_time: datetime
    owner_id: int
    owner: UserBase
    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    username: str
    avatar: str
    background: str
    images: list[ImageOut] = []
    
    class Config:
        orm_mode = True

