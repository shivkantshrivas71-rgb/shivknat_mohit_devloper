from datetime import datetime, timedelta, timezone
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

from database import get_user_collection
from models import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserProfileResponse,
    UpdateProfileRequest,
    RequestEmailVerification,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse
)
from chat import router as chat_router
from auth import (
    hash_password,
    verify_password,
    create_token,
    generate_otp,
    get_current_user
)

# 1. Initialize FastAPI Application
app = FastAPI(
    title="ChatBOT User Authentication & Chat API",
    description="User Registration, Email Verification, Login with JWT, Profile Management, Password Reset, and ChatGPT Chat Backend.",
    version="1.2.0"
)

# 2. Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount Modular Chat Backend Router
app.include_router(chat_router)


# -------------------------------------------------------------
# 3. Health & Information Route
# -------------------------------------------------------------
@app.get("/", tags=["General"])
def home():
    """Return health check and API documentation link."""
    return {
        "status": "healthy",
        "message": "ChatBOT User Authentication API is running smoothly",
        "docs_url": "/docs"
    }


# -------------------------------------------------------------
# 4. User Registration
# -------------------------------------------------------------
@app.post(
    "/user/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"]
)
async def user_register(user_data: UserRegister):
    """Register a new user, hash password, and initiate email verification."""
    users = get_user_collection()
    email = user_data.email.strip().lower()

    # Check if user already exists
    existing_user = await users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Generate initial email verification OTP
    verification_otp = generate_otp()
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    now = datetime.now(timezone.utc)
    new_user = {
        "name": user_data.name.strip(),
        "email": email,
        "password": hash_password(user_data.password),
        "is_email_verified": False,
        "verification_otp": verification_otp,
        "verification_otp_expiry": otp_expiry,
        "token": None,
        "created_at": now,
        "updated_at": now
    }

    result = await users.insert_one(new_user)

    print(f"[EMAIL VERIFICATION OTP] Initial OTP for {email} is: {verification_otp}")

    return UserResponse(
        id=str(result.inserted_id),
        name=new_user["name"],
        email=new_user["email"],
        is_email_verified=False
    )


# -------------------------------------------------------------
# 5. Email Verification - Request OTP
# -------------------------------------------------------------
@app.post(
    "/user/verify-email/request",
    response_model=MessageResponse,
    tags=["Email Verification"]
)
async def request_email_verification_otp(payload: RequestEmailVerification):
    """Send or regenerate an email verification OTP for the given email."""
    users = get_user_collection()
    email = payload.email.strip().lower()

    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address"
        )

    if user.get("is_email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already verified"
        )

    otp = generate_otp()
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    await users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "verification_otp": otp,
                "verification_otp_expiry": otp_expiry
            }
        }
    )

    print(f"[EMAIL VERIFICATION OTP] Verification OTP for {email} is: {otp}")

    return MessageResponse(
        message="Verification OTP has been generated successfully. It is valid for 10 minutes.",
        otp=otp
    )


# -------------------------------------------------------------
# 6. Email Verification - Confirm OTP
# -------------------------------------------------------------
@app.post(
    "/user/verify-email",
    response_model=MessageResponse,
    tags=["Email Verification"]
)
async def verify_email(payload: VerifyEmailRequest):
    """Verify email address using the received OTP."""
    users = get_user_collection()
    email = payload.email.strip().lower()

    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address"
        )

    if user.get("is_email_verified", False):
        return MessageResponse(message="Email is already verified.")

    saved_otp = user.get("verification_otp")
    otp_expiry = user.get("verification_otp_expiry")

    if not saved_otp or not otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active verification OTP found. Please request a new OTP."
        )

    # Ensure timezone-aware datetime comparison
    now = datetime.now(timezone.utc)
    if otp_expiry.tzinfo is None:
        otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)

    if now > otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification OTP has expired. Please request a new OTP."
        )

    if saved_otp != payload.otp.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification OTP."
        )

    # Mark email as verified and clear OTP fields
    await users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"is_email_verified": True, "updated_at": now},
            "$unset": {"verification_otp": "", "verification_otp_expiry": ""}
        }
    )

    return MessageResponse(message="Email address verified successfully.")


# -------------------------------------------------------------
# 7. User Login
# -------------------------------------------------------------
@app.post(
    "/user/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    tags=["Authentication"]
)
async def user_login(user_data: UserLogin):
    """Authenticate user with email and password, returning JWT bearer token."""
    users = get_user_collection()
    email = user_data.email.strip().lower()

    # Find user record
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Validate password
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT Token
    token = create_token(str(user["_id"]), user["email"])

    # Persist session token in MongoDB
    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"token": token}}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            is_email_verified=user.get("is_email_verified", False)
        )
    )


# -------------------------------------------------------------
# 8. User Profile - View
# -------------------------------------------------------------
@app.get(
    "/user/profile",
    response_model=UserProfileResponse,
    tags=["Profile"]
)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Retrieve profile information for the authenticated user."""
    created_at_val = current_user.get("created_at")
    created_at_str = created_at_val.isoformat() if created_at_val else None

    updated_at_val = current_user.get("updated_at")
    updated_at_str = updated_at_val.isoformat() if updated_at_val else None

    return UserProfileResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        is_email_verified=current_user.get("is_email_verified", False),
        created_at=created_at_str,
        updated_at=updated_at_str
    )


# -------------------------------------------------------------
# 9. User Profile - Update
# -------------------------------------------------------------
@app.put(
    "/user/profile",
    response_model=UserProfileResponse,
    tags=["Profile"]
)
async def update_user_profile(
    payload: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update profile information (e.g. name) for the authenticated user."""
    users = get_user_collection()
    updates = {}

    if payload.name is not None:
        clean_name = payload.name.strip()
        if not clean_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty"
            )
        updates["name"] = clean_name

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update"
        )

    now = datetime.now(timezone.utc)
    updates["updated_at"] = now

    await users.update_one(
        {"_id": current_user["_id"]},
        {"$set": updates}
    )

    # Fetch updated user document
    updated_user = await users.find_one({"_id": current_user["_id"]})

    created_at_val = updated_user.get("created_at")
    created_at_str = created_at_val.isoformat() if created_at_val else None

    updated_at_val = updated_user.get("updated_at")
    updated_at_str = updated_at_val.isoformat() if updated_at_val else None

    return UserProfileResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        is_email_verified=updated_user.get("is_email_verified", False),
        created_at=created_at_str,
        updated_at=updated_at_str
    )


# -------------------------------------------------------------
# 10. Forgot Password - Request OTP
# -------------------------------------------------------------
@app.post(
    "/user/forgot-password",
    response_model=MessageResponse,
    tags=["Password Reset"]
)
async def forgot_password(payload: ForgotPasswordRequest):
    """Generate a password reset OTP valid for 10 minutes."""
    users = get_user_collection()
    email = payload.email.strip().lower()

    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address"
        )

    otp = generate_otp()
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"reset_otp": otp, "otp_expiry": otp_expiry}}
    )

    print(f"[PASSWORD RESET OTP] OTP for {email} is: {otp}")

    return MessageResponse(
        message="Password reset OTP generated successfully. It is valid for 10 minutes.",
        otp=otp
    )


# -------------------------------------------------------------
# 11. Reset Password - Verify OTP & Set New Password
# -------------------------------------------------------------
@app.post(
    "/user/reset-password",
    response_model=MessageResponse,
    tags=["Password Reset"]
)
async def reset_password(payload: ResetPasswordRequest):
    """Verify OTP and update user password."""
    users = get_user_collection()
    email = payload.email.strip().lower()

    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    saved_otp = user.get("reset_otp")
    otp_expiry = user.get("otp_expiry")

    if not saved_otp or not otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active password reset request found. Please request an OTP first."
        )

    now = datetime.now(timezone.utc)
    if otp_expiry.tzinfo is None:
        otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)

    if now > otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset OTP has expired. Please request a new OTP."
        )

    if saved_otp != payload.otp.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP."
        )

    hashed_new_password = hash_password(payload.new_password)

    await users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password": hashed_new_password,
                "token": None,
                "updated_at": now
            },
            "$unset": {"reset_otp": "", "otp_expiry": ""}
        }
    )

    return MessageResponse(
        message="Password has been reset successfully. Please log in with your new password."
    )


# -------------------------------------------------------------
# 12. Local Application Runner
# -------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
