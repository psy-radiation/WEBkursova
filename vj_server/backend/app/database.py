import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Загружаем переменную окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём движок и сессию
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Создаём базовый класс для моделей
Base = declarative_base()
