from datetime import timedelta
from typing import Any
from sqlalchemy import select, delete, update, and_, or_
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
import bcrypt
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token, TokenPayload
from app.schemas.user import *
from app.api import deps
from app.core.security import *

router = APIRouter()

@router.post("/login")
def signin_user(
    db: Session,
    user_data: UserSigninSchema,
    response: Response
):
    existing_user = db.execute(select(User).where(User.id == user_data.id)).scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    verify_password = bcrypt.checkpw(user_data.password.encode("utf-8"), existing_user.password.encode("utf-8"))
    if not verify_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong credentials used to login")
    try:
        user_tokens_data = {
            "sub": existing_user.id,
            "username": existing_user.username
        }
        
        user_tokens = generate_user_tokens(user_tokens_data)
        
        response.set_cookie(
            key="access_token",
            value=user_tokens["access_token"],
            max_age=3600,
            expires=timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            path="/",
            secure=False,
            httponly=False,
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=user_tokens["refresh_token"],
            max_age=3600,
            expires=timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS),
            path="/",
            secure=False,
            httponly=False,
            samesite="lax"
        )
        
        return { "message": "User has been logged in" }
        
    except Exception as e:
        print(f"Unable to signin the user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to signin")



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
             
    except (jwt.JWTError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user = db.query(User).filter(User.id == str(token_data.sub)).first()
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


@router.post("/refresh")
def refresh_user_tokens(
    db: Session,
    request: Request,
    response: Response
):
    user_token = request.cookies.get("access_token")
    if not user_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token is not present so we cannot refresh")
    
    current_user = db.execute(select(User).where(User.id == user_token.get("sub"))).scalar_one_or_none()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="request User not found")
    
    try:
        user_tokens_data = {
            "sub": current_user.id,
            "username": current_user.username
        }
        
        user_tokens = generate_user_tokens(user_tokens_data)
        
        response.set_cookie(
            key="access_token",
            value=user_tokens["access_token"],
            max_age=3600,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            path="/",
            domain="/",
            secure=False,
            httponly=False,
            samesite="lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=user_tokens["refresh_token"]
        )
        
        
    except Exception as e:
        print(f"There was an error refreshing the tokens: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error lol")

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponseSchema)
def read_users_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user

@router.post("/register", response_model=UserResponseSchema)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserSignupSchema,
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
