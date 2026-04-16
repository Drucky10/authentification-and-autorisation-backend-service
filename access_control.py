from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, User
from auth import get_current_user

def has_permission(db: Session, user: User, resource: str, action: str) -> bool:
    if not user:
        return False
    for role in user.roles:
        for perm in role.permissions:
            if perm.resource == resource and perm.action == action:
                return True
    return False

def require_permission(resource: str, action: str):
    def dependency(user: User = Depends(get_current_user), db: Session = Depends(lambda: SessionLocal())):
        if not has_permission(db, user, resource, action):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return dependency