# routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal, User
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class RegisterRequest(BaseModel):
    email: str
    full_name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(lambda: SessionLocal())):
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        if existing_user.is_deleted:
            raise HTTPException(status_code=400, detail="This email was deleted. Contact support.")
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        email=req.email, 
        full_name=req.full_name, 
        password_hash=hash_password(req.password),
        is_deleted=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"msg": "User registered successfully", "user_id": user.id}

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.email == req.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.is_deleted:
        raise HTTPException(status_code=401, detail="Account has been deleted")
    
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.email)
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }

@router.post("/logout")
def logout():
    return {"msg": "Logged out successfully"}

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id, 
        "email": user.email, 
        "full_name": user.full_name,
        "is_deleted": user.is_deleted,
        "roles": [role.name for role in user.roles]
    }

@router.put("/me")
def update_me(
    req: UpdateUserRequest, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(lambda: SessionLocal())
):
    if user.is_deleted:
        raise HTTPException(status_code=400, detail="Account is deleted, cannot update")
    
    # Обновляем пользователя
    if req.full_name:
        user.full_name = req.full_name
    if req.password:
        if len(req.password) < 6:
            raise HTTPException(status_code=400, detail="Password too short (min 6 characters)")
        user.password_hash = hash_password(req.password)
    
    # Принудительно помечаем как измененный
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "msg": "User updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@router.delete("/me")
def delete_me(
    user: User = Depends(get_current_user), 
    db: Session = Depends(lambda: SessionLocal())
):
    """
    Мягкое удаление аккаунта через прямой UPDATE запрос
    """
    print(f"=== УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ===")
    print(f"User email: {user.email}")
    print(f"User ID: {user.id}")
    
    if user.is_deleted:
        raise HTTPException(status_code=400, detail="Account already deleted")
    
    # Прямой UPDATE запрос (обход проблем с сессиями)
    db.query(User).filter(User.id == user.id).update({"is_deleted": True})
    db.commit()
    
    print(f"=== УДАЛЕНИЕ ЗАВЕРШЕНО ===")
    
    return {
        "msg": "Account soft-deleted successfully",
        "info": "You have been logged out. Your account is deactivated.",
        "email": user.email,
        "status": "deleted"
    }