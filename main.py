from fastapi import FastAPI
from database import Base, engine, SessionLocal
from routes import users, admin, mock_resources
from database import Role, Permission, User
from config import Config
import bcrypt

# Создаем таблицы в PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Custom Auth System",
    description="RBAC система ",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(mock_resources.router)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@app.on_event ("startup")
def init_database():
    db = SessionLocal()
    
    if not db.query(Role).first():
        print("\n" + "="*50)
        print("🚀 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ РАЗГРАНИЧЕНИЯ ДОСТУПА")
        print("="*50 + "\n")
        
        # 1. Создаем роли
        roles_data = {
            "admin": "Полный доступ ко всем ресурсам",
            "manager": "Управление документами и просмотр отчетов",
            "viewer": "Только просмотр документов"
        }
        
        roles = {}
        for role_name in roles_data:
            role = Role(name=role_name)
            db.add(role)
            roles[role_name] = role
        db.commit()
        print("✅ Роли созданы:", list(roles_data.keys()))
        
        # 2. Создаем права доступа
        permissions_data = [
            # Ресурс: документы
            ("document", "read"), ("document", "create"), 
            ("document", "update"), ("document", "delete"),
            # Ресурс: заказы
            ("order", "read"), ("order", "create"),
            # Ресурс: отчеты
            ("report", "read"), ("report", "create"),
            # Ресурс: пользователи (только для админа)
            ("user", "manage")
        ]
        
        permissions = {}
        for resource, action in permissions_data:
            perm = Permission(resource=resource, action=action)
            db.add(perm)
            permissions[f"{resource}:{action}"] = perm
        db.commit()
        print("✅ Права созданы:", len(permissions_data), "штук\n")
        
        # 3. Назначаем права ролям
        print("📋 Назначение прав ролям:")
        
        # Админ - все права
        for perm in permissions.values():
            roles["admin"].permissions.append(perm)
        print("  • admin → все права")
        
        # Менеджер - документы (кроме delete) + отчеты
        manager_perms = [
            permissions["document:read"],
            permissions["document:create"],
            permissions["document:update"],
            permissions["report:read"]
        ]
        for perm in manager_perms:
            roles["manager"].permissions.append(perm)
        print("  • manager → document:read/create/update, report:read")
        
        # Зритель - только чтение документов
        roles["viewer"].permissions.append(permissions["document:read"])
        print("  • viewer → document:read\n")
        
        # 4. Создаем тестовых пользователей
        print("👤 Создание тестовых пользователей:")
        
        admin_user = User(
            email=Config.TEST_ADMIN_EMAIL,
            full_name="Администратор Системы",
            password_hash=hash_password(Config.TEST_ADMIN_PASSWORD)
        )
        admin_user.roles.append(roles["admin"])
        db.add(admin_user)
        print(f"  • Админ: {Config.TEST_ADMIN_EMAIL} / {Config.TEST_ADMIN_PASSWORD}")
        
        manager_user = User(
            email=Config.TEST_MANAGER_EMAIL,
            full_name="Менеджер Проектов",
            password_hash=hash_password(Config.TEST_MANAGER_PASSWORD)
        )
        manager_user.roles.append(roles["manager"])
        db.add(manager_user)
        print(f"  • Менеджер: manager@example.com / manager123")
        
        viewer_user = User(
            email=Config.TEST_USER_EMAIL,
            full_name="Обычный Пользователь",
            password_hash=hash_password(Config.TEST_USER_PASSWORD)
        )
        viewer_user.roles.append(roles["viewer"])
        db.add(viewer_user)
        print(f"  • Зритель: {Config.TEST_USER_EMAIL} / {Config.TEST_USER_PASSWORD}")
        
        db.commit()
        
        print("\n" + "="*50)
        print("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА")
        print("="*50 + "\n")
    
    db.close()

@app.get("/")
def root():
    return {
        "message": "Custom Auth System with PostgreSQL",
        "documentation": "/docs",
        "test_accounts": {
            "admin": "admin@example.com / admin123",
            "manager": "manager@example.com / manager123",
            "viewer": "user@example.com / user123"
        }
    }