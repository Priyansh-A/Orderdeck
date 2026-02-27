from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import SessionDep
from .. import schemas, models, utils, auth
from sqlmodel import select

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
async def login(
    session: SessionDep, 
    user_credentials: OAuth2PasswordRequestForm = Depends()
):
    query = select(models.User).where(models.User.username == user_credentials.username)
    result = await session.exec(query)
    user = result.first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )    
    
    access_token = auth.create_access_token(
        data={"user_id": user.id, "role": user.role}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user: auth.CurrentActiveUser):
    """Get current authenticated user"""
    return current_user