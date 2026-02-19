from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, User as UserSchema
from app.api import deps

router = APIRouter()

@router.post("/login")
def login_access_token(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    refresh_token = security.create_refresh_token(user.id)
    
    # Set Cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=settings.HTTP_ONLY,
        secure=settings.SECURE_COOKIES,
        samesite=settings.SAME_SITE,
        domain=settings.DOMAIN,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.HTTP_ONLY,
        secure=settings.SECURE_COOKIES,
        samesite=settings.SAME_SITE,
        domain=settings.DOMAIN,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {"message": "Login successful"}

@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
) -> Any:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if payload.get("type") != "refresh":
             raise HTTPException(status_code=401, detail="Invalid token type")
             
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Rotate tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    new_refresh_token = security.create_refresh_token(user.id)
    
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=settings.HTTP_ONLY,
        secure=settings.SECURE_COOKIES,
        samesite=settings.SAME_SITE,
        domain=settings.DOMAIN,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=settings.HTTP_ONLY,
        secure=settings.SECURE_COOKIES,
        samesite=settings.SAME_SITE,
        domain=settings.DOMAIN,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {"message": "Token refreshed"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this user name already exists in the system",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
