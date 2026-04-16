from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import Config

engine = create_engine(Config.DATABASE_URL, echo=False)  # echo=True видно SQL запросы
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Таблицы связи
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id")),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)
    is_deleted = Column(Boolean, default=False)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    resource = Column(String)
    action = Column(String)
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")