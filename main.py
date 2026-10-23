from datetime import datetime, timezone
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database import get_user_collection
from models import UserRegister, UserLogin, UserResponse, TokenResponse
from auth import hash_password, verify_password, create_token

# 1. FastAPI App Initialize
app = FastAPI(title="ChatBOT Auth API")

# 2. CORS Allow All
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Home Route
@app.get("/", tags=["Home"])
def home():
    return {"message": "ChatBOT Auth API is running", "docs": "/docs"}


# 4. User Register API Endpoint
@app.post(
    "/user/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User"]
)
@app.post(
    "/api/user/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
async def user_register(user_data: UserRegister):
    users = get_user_collection()
    email = user_data.email.strip().lower()

    # Check if user email already exists
    existing_user = await users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password and save to MongoDB
    new_user = {
        "name": user_data.name.strip(),
        "email": email,
        "password": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc)
    }

    result = await users.insert_one(new_user)

    return UserResponse(
        id=str(result.inserted_id),
        name=new_user["name"],
        email=new_user["email"]
    )


# 5. User Login API Endpoint
@app.post(
    "/user/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    tags=["User"]
)
@app.post(
    "/api/user/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
async def user_login(user_data: UserLogin):
    users = get_user_collection()
    email = user_data.email.strip().lower()

    # Find user by email
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check password match
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT Token
    token = create_token(str(user["_id"]), user["email"])

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"]
        )
    )


# 6. Run Server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
