import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Секретные ключи
    SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-2024")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
    
    # PostgreSQL подключение (измени пароль на свой)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password_here")  # Введи свой пароль
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "auth_system")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Тестовые данные
    TEST_ADMIN_EMAIL = "admin@example.com"
    TEST_ADMIN_PASSWORD = "admin123"
    TEST_USER_EMAIL = "user@example.com"
    TEST_USER_PASSWORD = "user123"
    TEST_MANAGER_EMAIL = "manager@example.com"
    TEST_MANAGER_PASSWORD = "manager123"