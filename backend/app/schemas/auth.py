from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    role: str = "user"
    user_id: int = 1


class TokenPayload(BaseModel):
    """Decoded JWT payload."""
    sub: Optional[str] = None
    role: Optional[str] = "user"


class RefreshTokenRequest(BaseModel):
    """Refresh token request body."""
    refresh_token: str


class UserLogin(BaseModel):
    """Login request body."""
    email: str
    password: str


class UserCreate(BaseModel):
    """User registration request body."""
    email: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    """User profile update request."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    """User response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str
