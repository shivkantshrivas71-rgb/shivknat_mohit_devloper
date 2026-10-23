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

# 4. Model for Login Token Response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
