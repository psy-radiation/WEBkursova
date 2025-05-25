from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from .. import models, database, schemas, auth
import shutil, os
from datetime import datetime

router = APIRouter(prefix="/images", tags=["Images"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=schemas.ImageOut)
async def upload_image(title: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    filename = f"{datetime.utcnow().timestamp()}_{file.filename}"
    # UPLOAD_DIR уже должен быть определен глобально и импортирован, если роутер в другом файле
    # или передан в функцию/класс роутера
    filepath = os.path.join(UPLOAD_DIR, filename) # Убедитесь, что UPLOAD_DIR здесь тот же самый

    print(f"Attempting to save file to: {filepath}") # <--- ДОБАВЬТЕ ДЛЯ ДЕБАГА

    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"File {filename} saved successfully to {filepath}") # <--- ДОБАВЬТЕ ДЛЯ ДЕБАГА
    except Exception as e:
        print(f"Error saving file: {e}") # <--- ДОБАВЬТЕ ДЛЯ ДЕБАГА
        # Можно возбудить HTTPException, если сохранение не удалось
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")


    image = models.Image(title=title, filename=filename, owner_id=current_user.id) 
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

@router.get("/latest", response_model=list[schemas.ImageOut])
def get_images(db: Session = Depends(get_db)):
    return db.query(models.Image).order_by(models.Image.upload_time.desc()).limit(10).all()
    
@router.get("/latestfr/{user_id}", response_model=list[schemas.ImageOut])
def get_images(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Image)\
             .filter(models.Image.owner_id == user_id)\
             .order_by(models.Image.upload_time.desc())\
             .limit(10)\
             .all()


@router.get("/{image_id}", response_model=schemas.ImageOut)
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image