from datetime import datetime, timedelta, timezone
import base64
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Response
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
    UserSettingsResponse,
    UpdateSettingsRequest,
    UploadPhotoResponse,
    RequestEmailVerification,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
    GoogleAuthRequest
)
from router.chat_router import router as chat_router
from auth import (
    hash_password,
    verify_password,
    create_token,
    generate_otp,
    get_current_user
)
from services.email_service import send_otp_email

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

import os
import time
from fastapi.staticfiles import StaticFiles

# 3. Mount Modular Chat Backend Router
app.include_router(chat_router)

# 3a. Mount Static Files Directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------------------------------------------
# 3b. Rotating Banner Image API (Changes every 2 seconds)
# -------------------------------------------------------------
BANNER_SLIDES = [
    {
        "id": 1,
        "title": "GPT-6 with Intelligent UI",
        "subtitle": "Get visual and interactive answers to help you take the next step",
        "image_url": "/static/purple_chart.png",
        "action_text": "Try GPT-6",
        "prompt": "Explain GPT-6 with Intelligent UI and provide interactive visual insights."
    },
    {
        "id": 2,
        "title": "Deep Reasoning & Thinking Mode",
        "subtitle": "Solve complex coding, math, and architecture problems with step-by-step logic",
        "image_url": "/static/reasoning_chart.png",
        "action_text": "Try Think Mode",
        "prompt": "Demonstrate deep reasoning step-by-step logic to build a modern scalable web application."
    },
    {
        "id": 3,
        "title": "Advanced Multimodal AI",
        "subtitle": "Attach photos, PDFs, videos, or AI files and analyze instantly",
        "image_url": "/static/multimodal_chart.png",
        "action_text": "Explore Files",
        "prompt": "How can I analyze complex images, PDFs and datasets using multimodal AI?"
    }
]

@app.get("/banner/current", tags=["Banner"])
def get_current_banner():
    """Returns the active showcase banner card. Automatically rotates every 2 seconds."""
    idx = int(time.time() // 2) % len(BANNER_SLIDES)
    item = BANNER_SLIDES[idx].copy()
    item["rotation_interval_seconds"] = 2
    item["server_timestamp"] = time.time()
    return item

@app.get("/banner/slides", tags=["Banner"])
def get_all_banner_slides():
    """Returns all showcase banner slides."""
    return {"slides": BANNER_SLIDES, "rotation_interval_seconds": 2}


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

    # Dispatch OTP via real SMTP email service
    send_otp_email(email, verification_otp, purpose="Account Registration Verification")

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

    # Dispatch OTP via real SMTP email service
    send_otp_email(email, otp, purpose="Email Verification")

    return MessageResponse(
        message="Verification OTP has been sent to your email. It is valid for 10 minutes.",
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
# 7b. Google Authentication (Sign in with Google)
# -------------------------------------------------------------
@app.post(
    "/user/google-auth",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Login or register user with Google"
)
async def user_google_auth(payload: GoogleAuthRequest):
    """Authenticate or create user using Google Account."""
    users = get_user_collection()
    email = payload.email.strip().lower()
    now = datetime.now(timezone.utc)

    user = await users.find_one({"email": email})
    if not user:
        new_user = {
            "name": payload.name or "Google User",
            "email": email,
            "password": hash_password(f"google_oauth_{payload.google_id or email}"),
            "is_email_verified": True,
            "google_id": payload.google_id,
            "avatar_url": payload.avatar_url,
            "token": None,
            "created_at": now,
            "updated_at": now
        }
        res = await users.insert_one(new_user)
        user_id = str(res.inserted_id)
        user_name = new_user["name"]
    else:
        user_id = str(user["_id"])
        user_name = user["name"]
        updates = {"updated_at": now, "is_email_verified": True}
        if payload.google_id:
            updates["google_id"] = payload.google_id
        if payload.avatar_url and not user.get("avatar_url"):
            updates["avatar_url"] = payload.avatar_url
        await users.update_one({"_id": user["_id"]}, {"$set": updates})

    token = create_token(user_id, email)
    await users.update_one({"email": email}, {"$set": {"token": token}})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            name=user_name,
            email=email,
            is_email_verified=True
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

    user_id_str = str(current_user["_id"])
    avatar_url = current_user.get("avatar_url") or (f"/user/profile/photo/{user_id_str}" if current_user.get("avatar_base64") else None)

    return UserProfileResponse(
        id=user_id_str,
        name=current_user["name"],
        email=current_user["email"],
        surname=current_user.get("surname", ""),
        gender=current_user.get("gender", "Male"),
        avatar_url=avatar_url,
        is_email_verified=current_user.get("is_email_verified", False),
        created_at=created_at_str,
        updated_at=updated_at_str
    )


# -------------------------------------------------------------
# 9. User Profile - Update (Name, Surname, Gender)
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
    """Update profile information (e.g. name, surname, gender) for the authenticated user."""
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

    if payload.surname is not None:
        updates["surname"] = payload.surname.strip()

    if payload.gender is not None:
        updates["gender"] = payload.gender.strip()

    if payload.avatar_base64 is not None:
        updates["avatar_base64"] = payload.avatar_base64
        updates["avatar_url"] = f"/user/profile/photo/{str(current_user['_id'])}"

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

    user_id_str = str(updated_user["_id"])
    avatar_url = updated_user.get("avatar_url") or (f"/user/profile/photo/{user_id_str}" if updated_user.get("avatar_base64") else None)

    return UserProfileResponse(
        id=user_id_str,
        name=updated_user["name"],
        email=updated_user["email"],
        surname=updated_user.get("surname", ""),
        gender=updated_user.get("gender", "Male"),
        avatar_url=avatar_url,
        is_email_verified=updated_user.get("is_email_verified", False),
        created_at=created_at_str,
        updated_at=updated_at_str
    )


# -------------------------------------------------------------
# 9b. User Profile - Photo Upload API
# -------------------------------------------------------------
@app.post(
    "/user/profile/photo",
    response_model=UploadPhotoResponse,
    tags=["Profile"]
)
async def upload_user_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and persist user profile avatar photo into MongoDB cloud.
    """
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Allowed: PNG, JPEG, WEBP."
        )

    photo_bytes = await file.read()
    if len(photo_bytes) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile photo exceeds 5MB size limit."
        )

    base64_str = base64.b64encode(photo_bytes).decode("utf-8")
    user_id_str = str(current_user["_id"])
    avatar_url = f"/user/profile/photo/{user_id_str}"

    users = get_user_collection()
    await users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "avatar_base64": base64_str,
                "avatar_content_type": file.content_type,
                "avatar_url": avatar_url,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return UploadPhotoResponse(
        message="Profile photo updated successfully in MongoDB Atlas",
        avatar_url=avatar_url
    )


# -------------------------------------------------------------
# 9c. User Profile - Photo Fetch API (Public Binary Image)
# -------------------------------------------------------------
@app.get(
    "/user/profile/photo/{user_id}",
    tags=["Profile"],
    summary="Get user profile picture binary stream"
)
async def get_user_photo(user_id: str):
    """
    Returns the binary image data of a user's uploaded avatar.
    """
    users = get_user_collection()
    clean_id = user_id.strip()
    u_filter = {"_id": ObjectId(clean_id)} if ObjectId.is_valid(clean_id) else {"_id": clean_id}

    user = await users.find_one(u_filter)
    if not user or not user.get("avatar_base64"):
        raise HTTPException(status_code=404, detail="Profile picture not found.")

    raw_bytes = base64.b64decode(user["avatar_base64"])
    c_type = user.get("avatar_content_type", "image/png")
    return Response(content=raw_bytes, media_type=c_type)


# -------------------------------------------------------------
# 9d. User Settings API (Preferences for Three-Dot Menu)
# -------------------------------------------------------------
@app.get(
    "/user/settings",
    response_model=UserSettingsResponse,
    tags=["Settings"],
    summary="Retrieve user configuration settings"
)
async def get_user_settings(current_user: dict = Depends(get_current_user)):
    """Fetch user preferences (theme, model, speech speed)."""
    settings = current_user.get("settings", {})
    return UserSettingsResponse(
        selected_model=settings.get("selected_model", "openai/gpt-4o-mini"),
        theme=settings.get("theme", "light"),
        voice_speed=settings.get("voice_speed", 1.0),
        system_prompt=settings.get("system_prompt", None)
    )


@app.put(
    "/user/settings",
    response_model=UserSettingsResponse,
    tags=["Settings"],
    summary="Update user configuration settings"
)
async def update_user_settings(
    payload: UpdateSettingsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save user preferences in MongoDB Atlas."""
    users = get_user_collection()
    existing_settings = current_user.get("settings", {})

    if payload.selected_model is not None:
        existing_settings["selected_model"] = payload.selected_model
    if payload.theme is not None:
        existing_settings["theme"] = payload.theme
    if payload.voice_speed is not None:
        existing_settings["voice_speed"] = payload.voice_speed
    if payload.system_prompt is not None:
        existing_settings["system_prompt"] = payload.system_prompt

    await users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "settings": existing_settings,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return UserSettingsResponse(
        selected_model=existing_settings.get("selected_model", "openai/gpt-4o-mini"),
        theme=existing_settings.get("theme", "light"),
        voice_speed=existing_settings.get("voice_speed", 1.0),
        system_prompt=existing_settings.get("system_prompt", None)
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

    # Dispatch OTP via real SMTP email service
    send_otp_email(email, otp, purpose="Password Reset")

    return MessageResponse(
        message="Password reset OTP has been sent to your email. It is valid for 10 minutes.",
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
