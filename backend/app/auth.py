import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from .database import SessionDep
from . import schemas, models, config
from sqlmodel import select
from fastapi import Depends, HTTPException, status
from .permissions import *
from typing import List, Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = config.settings.SECRET_KEY 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        role = payload.get("role")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id, role=role)
    except InvalidTokenError:
        raise credentials_exception
    
    return token_data
    
async def get_current_user(
    session: SessionDep,
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    
    query = select(models.User).where(models.User.id == token_data.id)
    result = await session.exec(query)
    user = result.first()
    
    if user is None:
        raise credentials_exception
    return user

CurrentUser = Annotated[models.User, Depends(get_current_user)]

def get_current_active_user(
    current_user: CurrentUser
) -> models.User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

CurrentActiveUser = Annotated[models.User, Depends(get_current_active_user)]

def require_permissions(required_permissions: List[Permission]):
    async def permission_checker(
        current_user: CurrentActiveUser
    ) -> models.User:
        from .permissions import ROLE_PERMISSIONS
        
        if isinstance(current_user.role, str):
            try:
                role_enum = UserRole(current_user.role)
            except ValueError:
                role_enum = None
        else:
            role_enum = current_user.role
            
        user_permissions = ROLE_PERMISSIONS.get(role_enum, [])
        
        missing_permissions = [
            perm for perm in required_permissions 
            if perm not in user_permissions
        ]
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing_permissions}"
            )
        return current_user
    return permission_checker