from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
import shutil, os
from app import schemas, models, database, auth
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]

@router.get("/me", response_model=schemas.UserOut)
async def get_current_user(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

# Получение данных любого пользователя
@router.get("/{user_id}", response_model=schemas.UserOut)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(username=user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = models.User(
        username=user.username,
        password=auth.hash_password(user.password),
        background="defaultback",
        avatar="defaultav.png"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Registered"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(username=user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_token({"sub": db_user.username})
    return {"access_token": token}

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # 1. Проверка типа файла
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )

        # 2. Подготовка директории
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 3. Генерация имени файла
        ext = file.filename.split('.')[-1].lower()
        filename = f"avatar_{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}"
        filepath = os.path.abspath(os.path.join(UPLOAD_DIR, filename))

        # 4. Проверка безопасности пути
        if not filepath.startswith(os.path.abspath(UPLOAD_DIR)):
            raise HTTPException(
                status_code=400,
                detail="Invalid file path"
            )

        # 5. Сохранение файла
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 6. Удаление старого аватара
        old_avatar = None
        if current_user.avatar:
            old_avatar = os.path.join(UPLOAD_DIR, current_user.avatar)
            if os.path.exists(old_avatar):
                try:
                    os.remove(old_avatar)
                except Exception as e:
                    print(f"Warning: Could not delete old avatar: {str(e)}")
        try:
            user = db.merge(current_user)
            user.avatar = filename
            db.commit()
            db.refresh(user)
        except Exception as e:
            # Откатываем изменения в БД если ошибка
            db.rollback()
            # Удаляем только что сохранённый файл
            if os.path.exists(filepath):
                os.remove(filepath)
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

        return {
            "message": "Avatar uploaded successfully",
            "filename": filename,
            "avatar_url": f"/{UPLOAD_DIR}/{filename}"
        }

    except HTTPException:
        raise  # Пробрасываем уже обработанные ошибки
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
        
@router.post("/me/background")
async def upload_background(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверка типа файла
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG and GIF images are allowed")
    
    # Генерируем уникальное имя файла
    ext = file.filename.split('.')[-1]
    filename = f"bg_{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    try:
        # Сохраняем файл
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Удаляем старый фон, если он существует
        if current_user.background:
            old_filepath = os.path.join(UPLOAD_DIR, current_user.background)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
        
        # Обновляем пользователя в БД
        user = db.merge(current_user)
        user.background = filename
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Background uploaded successfully",
            "filename": filename,
            "background_url": f"/{UPLOAD_DIR}/{filename}"  # URL для доступа к фону
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload background: {str(e)}")