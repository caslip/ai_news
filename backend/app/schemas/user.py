from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class OAuthProvider(str, Enum):
    GITHUB = "github"
    GOOGLE = "google"


class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    nickname: str = Field(..., min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    push_config: Optional[dict] = None


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.USER
    push_config: dict = {}
    oauth_provider: Optional[OAuthProvider] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None
