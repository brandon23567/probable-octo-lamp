from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserResponseSchema(BaseModel):
    id: int
    username: str 
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)
    
    
class UserSignupSchema(BaseModel):
    username: str = Field(..., description="username")
    email: EmailStr = Field(..., description="user email")
    password: str = Field(..., description="password")
    
    model_config = ConfigDict(from_attributes=True)
    

class UserSigninSchema(BaseModel):
    username: str = Field(..., description="username for user to log in")
    password: str = Field(..., description="password for user to log in")
    
    model_config = ConfigDict(from_attributes=True)

# class UserBase(BaseModel):
#     email: EmailStr
#     is_active: Optional[bool] = True

# class UserCreate(UserBase):
#     password: str

# class UserUpdate(UserBase):
#     password: Optional[str] = None

# class UserInDBBase(UserBase):
#     id: Optional[int] = None

#     class Config:
#         from_attributes = True

# class User(UserInDBBase):
#     pass

# class UserInDB(UserInDBBase):
#     hashed_password: str
