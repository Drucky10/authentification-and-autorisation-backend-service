from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, Role, Permission, User
from access_control import require_permission

router = APIRouter(prefix="/admin", tags=["admin"])

class AssignPermissionRequest(BaseModel):
    role_name: str
    resource: str
    action: str

class CreateRoleRequest(BaseModel):
    role_name: str

class AssignRoleToUserRequest(BaseModel):
    user_email: str
    role_name: str

# ============ УПРАВЛЕНИЕ РОЛЯМИ ============
@router.get("/roles")
def list_roles(
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Список всех ролей"""
    roles = db.query(Role).all()
    return [
        {
            "id": r.id, 
            "name": r.name,
            "permissions": [f"{p.resource}:{p.action}" for p in r.permissions]
        } 
        for r in roles
    ]

@router.post("/roles")
def create_role(
    req: CreateRoleRequest,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Создать новую роль"""
    existing = db.query(Role).filter(Role.name == req.role_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    role = Role(name=req.role_name)
    db.add(role)
    db.commit()
    db.refresh(role)
    
    return {"msg": f"Role '{req.role_name}' created", "role_id": role.id}

@router.delete("/roles/{role_name}")
def delete_role(
    role_name: str,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Удалить роль"""
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(role)
    db.commit()
    return {"msg": f"Role '{role_name}' deleted"}

# ============ УПРАВЛЕНИЕ ПРАВАМИ ============
@router.get("/permissions")
def list_permissions(
    _=Depends(require_permission("user", "manage")), 
    db: Session = Depends(lambda: SessionLocal())
):
    """Список всех прав"""
    perms = db.query(Permission).all()
    return [{"id": p.id, "resource": p.resource, "action": p.action} for p in perms]

@router.post("/role-permissions")
def add_permission_to_role(
    req: AssignPermissionRequest,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Назначить право роли"""
    role = db.query(Role).filter(Role.name == req.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    perm = db.query(Permission).filter(
        Permission.resource == req.resource, 
        Permission.action == req.action
    ).first()
    
    if not perm:
        perm = Permission(resource=req.resource, action=req.action)
        db.add(perm)
        db.commit()
        db.refresh(perm)
    
    if perm not in role.permissions:
        role.permissions.append(perm)
        db.commit()
    
    return {
        "msg": f"Permission '{req.action}:{req.resource}' granted to role '{req.role_name}'",
        "role": req.role_name,
        "permission": f"{req.resource}:{req.action}"
    }

@router.delete("/role-permissions")
def remove_permission_from_role(
    req: AssignPermissionRequest,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Отозвать право у роли"""
    role = db.query(Role).filter(Role.name == req.role_name).first()
    perm = db.query(Permission).filter(
        Permission.resource == req.resource, 
        Permission.action == req.action
    ).first()
    
    if role and perm and perm in role.permissions:
        role.permissions.remove(perm)
        db.commit()
    
    return {"msg": f"Permission revoked from role '{req.role_name}'"}

# ============ УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ============
@router.post("/assign-role")
def uassign_role_to_user(
    req: AssignRoleToUserRequest,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """
    Назначить роль пользователю (только для администраторов)
    
    - **user_email**: Email пользователя
    - **role_name**: Название роли (admin, manager, viewer или созданная)
    """
    # Ищем пользователя
    user = db.query(User).filter(
        User.email == req.user_email, 
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{req.user_email}' not found")
    
    # Ищем роль
    role = db.query(Role).filter(Role.name == req.role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"Role '{req.role_name}' not found")
    
    # Назначаем роль
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)
        
        return {
            "msg": f"Role '{req.role_name}' assigned to user '{req.user_email}'",
            "user_email": user.email,
            "user_roles": [r.name for r in user.roles],
            "assigned_role": req.role_name
        }
    else:
        return {
            "msg": f"User '{req.user_email}' already has role '{req.role_name}'",
            "user_email": user.email,
            "user_roles": [r.name for r in user.roles]
        }

@router.get("/user-roles/{user_email}")
def get_user_roles(
    user_email: str,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Получить все роли пользователя"""
    user = db.query(User).filter(
        User.email == user_email, 
        User.is_deleted == False
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_email": user.email,
        "user_full_name": user.full_name,
        "roles": [{"id": r.id, "name": r.name} for r in user.roles],
        "permissions": list(set([
            f"{p.resource}:{p.action}" 
            for r in user.roles 
            for p in r.permissions
        ]))
    }

@router.delete("/remove-role")
def remove_role_from_user(
    user_email: str,
    role_name: str,
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Удалить роль у пользователя"""
    user = db.query(User).filter(User.email == user_email, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
        return {"msg": f"Role '{role_name}' removed from user '{user_email}'"}
    
    return {"msg": f"User '{user_email}' does not have role '{role_name}'"}

@router.get("/users")
def list_all_users(
    _=Depends(require_permission("user", "manage")),
    db: Session = Depends(lambda: SessionLocal())
):
    """Список всех пользователей (только для админов)"""
    users = db.query(User).filter(User.is_deleted == False).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "roles": [r.name for r in u.roles]
        }
        for u in users
    ]