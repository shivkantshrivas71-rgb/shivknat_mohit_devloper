from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user", examples=["John Doe"])
    email: EmailStr = Field(..., description="Valid user email address", examples=["user@example.com"])
    password: str = Field(..., min_length=6, max_length=128, description="User password (min 6 characters)", examples=["SecurePassword123"])

class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., description="Registered user email", examples=["user@example.com"])
    password: str = Field(..., description="User password", examples=["SecurePassword123"])

class UserResponse(BaseModel):
    """Schema for public user profile response (excluding sensitive info)."""
    id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema for JWT token response on successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ApiResponse(BaseModel):
    """Standardized API response wrapper."""
    success: bool
    message: str
    data: Optional[dict] = None
