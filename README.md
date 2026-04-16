# Custom Authentication & Authorization System

## 📋 Описание проекта

Реализована собственная система аутентификации и авторизации через python и fastapi.

### 📚 Стек технологий
 FastAPI - веб-фреймворк
 SQLAlchemy - ORM
 PostgreSQL - база данных
JWT (python-jose) - токены
Passlib + bcrypt - хэширование паролей
Uvicorn - ASGI сервер

### Основные возможности:
- ✅ Регистрация, логин, logout пользователей
- ✅ Мягкое удаление аккаунта (is_deleted)
- ✅ Обновление профиля пользователя
- ✅ Собственная RBAC система (Role-Based Access Control)
- ✅ Разграничение доступа к ресурсам (ресурс + действие)
- ✅ JWT токены для аутентификации
- ✅ Админ API для управления правами доступа
- ✅ Mock-объекты для демонстрации бизнес-логики
- ✅ PostgreSQL база данных

---

## 🏗️ Архитектура системы

### Схема базы данных

```sql
users (id, email, full_name, password_hash, is_deleted)
    ↓
user_roles (user_id, role_id)
    ↓
roles (id, name)
    ↓
role_permissions (role_id, permission_id)
    ↓
permissions (id, resource, action)
```

## 🚀 Установка и запуск
1. Требования
    Python 3.12+
    PostgreSQL 16+

2. Установка зависимостей
#### Клонируйте проект
      cd "authentification-and-autorisation-backend-service"

# Установите зависимости
    pip install -r requirements.txt

3. Настройка базы данных PostgreSQL

#### -- Создайте базу данных
    CREATE DATABASE auth_system;

4. Настройка переменных окружения

Создайте файл .env в корне проекта и Скопируйте этот содержение

    SECRET_KEY=your-super-secret-key-change-in-production-2024
    ACCESS_TOKEN_EXPIRE_HOURS=24
    
    PostgreSQL подключение (измените под свои настройки)
    DB_USER=postgres
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=auth_system

5. Запуск приложения

 #### Запуск сервера
    uvicorn main:app --reload --host 127.0.0.1 --port 8000

6. Проверка запуска

Откройте в браузере: http://127.0.0.1:8000

Ожидаемый ответ:

    {
      "message": "Custom Auth System with PostgreSQL",
      "documentation": "/docs",
      "test_accounts": {
        "admin": "admin@example.com / admin123",
        "manager": "manager@example.com / manager123",
        "viewer": "user@example.com / user123"
      }
    }



## 🗄️ Тестовые учетные записи

  Роль	Email	Пароль
  Администратор	admin@example.com	admin123
  Менеджер	manager@example.com	manager123
  Зритель (Viewer)	user@example.com	user123

### 

<img width="678" height="218" alt="{123D568A-3179-43A9-BA89-9B2BAF19B3CD}" src="https://github.com/user-attachments/assets/39fdfbbb-3138-4ceb-9b10-29150aaf7bc2" />

<img width="408" height="211" alt="{1587C0E1-B6DC-4214-8940-4A06CAEFFD85}" src="https://github.com/user-attachments/assets/9d9c7e0f-a13c-41a8-ae14-c98a4efa4bb8" />



Версия: 1.0.0
Дата: 2026-04-11
Лицензия: нет
