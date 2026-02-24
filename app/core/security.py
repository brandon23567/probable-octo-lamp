from datetime import datetime, timedelta, timezone
from typing import Any, Union
import jwt
from passlib.context import CryptContext
from app.core.config import settings
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
#     to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt


# def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
#     to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt


def create_access_token(user_data: dict) -> str:
    try:
        access_token_data = user_data.copy()
        exp_time = datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_data.update({ "exp": exp_time, "type": "access" })
        
        access_token = jwt.encode(access_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return access_token
        
    except Exception as e:
        print(f"Unable to generate the access tokens:{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate access tokens"
        )
        
        
def create_refresh_token(user_data: dict) -> str:
    try:
        print("")
        
        refresh_token_data = user_data.copy()
        exp_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_data.update({ "exp": exp_time, "type": "refresh" })
        
        refresh_token = jwt.encode(refresh_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return refresh_token
            
    except Exception as e:
        print(f"There was an error trying to generate the refresh tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate refresh tokens"
        )


def generate_user_tokens(user_data: dict) -> dict:
    try:
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
    except Exception as e:
        print(f"Unable to generate the token pairs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate the token pairs"
        )

def decode_access_token(access_token: dict) -> dict:
    try:
        decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id = decoded_token.get("sub")
        username = decoded_token.get("username")
        
        return {
            "user_id": user_id,
            "username": username
        }
        
    except Exception as e:
        print(f"Unable to decode access token: str{e}")
        

# def generate_refresh_tokens():
#     pass

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
