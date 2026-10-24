from typing import Optional
from pydantic import BaseModel, EmailStr

# 1. Model for User Registration
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

# 2. Model for User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 3. Model for Public User Response
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    is_email_verified: bool = False

# 4. Model for Login Token Response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 5. Model for User Profile Response
class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    surname: Optional[str] = ""
    gender: Optional[str] = "Male"
    avatar_url: Optional[str] = None
    is_email_verified: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# 6. Model for Updating User Profile
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[str] = None
    avatar_base64: Optional[str] = None

# 6b. Model for User Settings (Preferences in Three-Dot Menu)
class UserSettingsResponse(BaseModel):
    selected_model: str = "openai/gpt-4o-mini"
    theme: str = "light"
    voice_speed: float = 1.0
    system_prompt: Optional[str] = None

class UpdateSettingsRequest(BaseModel):
    selected_model: Optional[str] = None
    theme: Optional[str] = None
    voice_speed: Optional[float] = None
    system_prompt: Optional[str] = None

class UploadPhotoResponse(BaseModel):
    message: str
    avatar_url: str

# 7. Model for Requesting Email Verification OTP
class RequestEmailVerification(BaseModel):
    email: EmailStr

# 8. Model for Confirming Email Verification with OTP
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

# 9. Model for Forgot Password (Request OTP)
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# 10. Model for Reset Password with OTP
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

# 11. Generic Message Response
class MessageResponse(BaseModel):
    message: str
    otp: Optional[str] = None
