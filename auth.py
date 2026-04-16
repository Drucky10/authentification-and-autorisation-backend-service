from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal, User
from config import Config

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

security = HTTPBearer()

def hash_password(password: str) -> str:
    if len(password) > 72:
        raise HTTPException(
            status_code=400, 
            detail="Password too long (max 72 characters)"
        )
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def create_access_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=Config.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), 
                     db: Session = Depends(lambda: SessionLocal())):
    """
    Получение текущего пользователя из токена
    """
    email = decode_token(token.credentials)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid authentication credentials",
        )
    
    # Получаем пользователя
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found",
        )
    
    # Логируем статус пользователя
    print(f"User {email} - is_deleted: {user.is_deleted}")
    
    # Проверка на удаление
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Account has been deleted",
        )
    
    return user