from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Використовуємо SQLite (файл database.db у корені проєкту)
DATABASE_URL = "sqlite:///C:/Users/yaros/OneDrive/Документи/GitHub/systems-Programming-2025/test.db"

# create_engine — створює конектор
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # ТІЛЬКИ ДЛЯ SQLite
)

# sessionmaker — фабрика сесій
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовий клас моделей SQLAlchemy
Base = declarative_base()


# Головна залежність FastAPI для роботи з БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
