from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.database import get_user_collection
from app.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a user with a valid name, valid email, and secure password. Stores encrypted info in MongoDB."
)
async def register_user(payload: UserRegisterRequest):
    users_collection = get_user_collection()
    normalized_email = payload.email.strip().lower()

    # Check if email is already taken
    existing_user = await users_collection.find_one({"email": normalized_email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Hash the password securely
    hashed_pwd = hash_password(payload.password)

    # Prepare document for MongoDB
    user_document = {
        "name": payload.name.strip(),
        "email": normalized_email,
        "password": hashed_pwd,
        "created_at": datetime.now(timezone.utc)
    }

    # Insert into database
    result = await users_collection.insert_one(user_document)

    return UserResponse(
        id=str(result.inserted_id),
        name=user_document["name"],
        email=user_document["email"],
        created_at=user_document["created_at"]
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticates a user with a valid email and password, returning a JWT bearer token."
)
async def login_user(payload: UserLoginRequest):
    users_collection = get_user_collection()
    normalized_email = payload.email.strip().lower()

    # Find user by email
    user = await users_collection.find_one({"email": normalized_email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Verify password against stored hash
    if not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Generate JWT token
    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "email": user["email"]
        }
    )

    user_info = UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"]
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_info
    )
