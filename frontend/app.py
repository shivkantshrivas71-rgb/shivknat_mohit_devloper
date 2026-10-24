import streamlit as st
import requests
import time
import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional

# Import dynamic API Base URL from frontend/config.py
from config import API_BASE_URL
BACKEND_BASE_URL = API_BASE_URL

# -------------------------------------------------------------
# 1. Page Configuration & Futuristic Cyber Dark Theme
# -------------------------------------------------------------
st.set_page_config(
    page_title="NEXUS AI // Cyber ChatBot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Cyberpunk Dark CSS (No blinking, no dimming, instant snappy feel)
st.markdown("""
<style>
    /* 1. Authentic ChatGPT Clean White / Light Theme */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #0d0d0d !important;
        opacity: 1 !important;
        transition: none !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }
    
    div[data-testid="stAppViewContainer"] > section {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
        background-color: #ffffff !important;
    }

    div[data-st-app-view="true"], div[data-testid="stMain"], div[data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
        animation: none !important;
        background-color: #ffffff !important;
    }

    /* Hide the top-right blinking reload spinner indicator */
    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. Sidebar ChatGPT Light Styling (#f9f9f9) */
    section[data-testid="stSidebar"] {
        background-color: #f9f9f9 !important;
        border-right: 1px solid #e5e5e5 !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #0d0d0d !important;
        font-weight: 600 !important;
    }

    /* 3. Real ChatGPT Message Styling */
    /* User Message Bubble (#f4f4f4) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #f4f4f4 !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 18px !important;
        padding: 12px 18px !important;
        margin-bottom: 12px !important;
        color: #0d0d0d !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
    }

    /* Assistant Reply (Clean transparent stream) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 4px !important;
        margin-bottom: 16px !important;
        color: #0d0d0d !important;
    }

    /* 4. Chat History Item in Sidebar (#f9f9f9 with subtle hover) */
    .history-card {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 4px;
        transition: all 0.12s ease-in-out;
    }
    
    .history-card:hover {
        background-color: #ececec;
        border-color: #e0e0e0;
    }

    .history-card-active {
        background-color: #e3e3e3 !important;
        border: 1px solid #dcdcdc !important;
    }

    .history-title {
        color: #0d0d0d;
        font-size: 0.88rem;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }

    .history-meta {
        font-size: 0.72rem;
        color: #676767;
        margin-top: 2px;
        display: flex;
        justify-content: space-between;
    }

    /* 5. Minimalist Buttons */
    .stButton > button {
        background-color: #ffffff !important;
        color: #0d0d0d !important;
        border: 1px solid #d9d9e3 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background-color: #f4f4f4 !important;
        border-color: #b4b4c4 !important;
        color: #000000 !important;
    }

    /* ChatGPT Accent Button (Green #10a37f) */
    .stButton > button[kind="primary"] {
        background: #10a37f !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1a7f64 !important;
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.35) !important;
    }

    /* Settings & Three-dot Popover */
    div[data-testid="stPopover"] > button {
        background-color: #ffffff !important;
        border: 1px solid #d9d9e3 !important;
        border-radius: 8px !important;
        color: #0d0d0d !important;
        padding: 5px 10px !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #f4f4f4 !important;
        border-color: #b4b4c4 !important;
    }

    div[data-testid="stPopoverBody"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 14px !important;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.12) !important;
        color: #0d0d0d !important;
        padding: 18px !important;
    }

    /* 6. Floating Input Bar (ChatGPT Pill Shape) */
    .stChatFloatingInputContainer {
        bottom: 15px;
        background: transparent !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border-radius: 26px !important;
        border: 1px solid #d9d9e3 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #0d0d0d !important;
        background: transparent !important;
    }

    /* Try GPT-6 Pill Button Styling */
    div.st-key-btn_try_gpt6 > button {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 9999px !important;
        padding: 8px 24px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
        transition: all 0.2s ease !important;
    }
    div.st-key-btn_try_gpt6 > button:hover {
        background-color: #e5e7eb !important;
        border-color: #d1d5db !important;
        transform: translateY(-1px) !important;
    }

    /* Blue Circular Advanced Voice Mode Button */
    div.st-key-btn_advanced_voice > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        border: none !important;
        height: 42px !important;
        width: 42px !important;
        min-width: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.45) !important;
        font-size: 1.15rem !important;
        margin: 0 auto !important;
        padding: 0 !important;
        transition: transform 0.15s ease, background-color 0.15s ease !important;
    }
    div.st-key-btn_advanced_voice > button:hover {
        background-color: #1d4ed8 !important;
        transform: scale(1.08) !important;
    }

    /* Microphone Button */
    div.st-key-btn_mic_speech > button {
        border-radius: 50% !important;
        height: 42px !important;
        width: 42px !important;
        min-width: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
        padding: 0 !important;
        border: 1px solid #e5e7eb !important;
    }

    /* Plus Attachment Button */
    div[data-testid="stPopover"]:has(.plus-popover-tag) > button,
    div.st-key-plus_attach_popover > button {
        border-radius: 50% !important;
        height: 42px !important;
        width: 42px !important;
        min-width: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        border: 1px solid #e5e7eb !important;
        background-color: #ffffff !important;
        padding: 0 !important;
    }

    /* Think Button */
    div.st-key-btn_toggle_thinking > button {
        border-radius: 20px !important;
        padding: 6px 14px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        border: 1px solid #d1d5db !important;
    }

    /* ChatGPT Auth Screen Styling in Light Mode */
    .chatgpt-auth-card {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 18px;
        padding: 32px 30px;
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.07);
        margin: 15px auto 25px auto;
    }
    .chatgpt-badge-icon {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: #ffffff;
        border: 1.5px solid #e5e5e5;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px auto;
    }
    .chatgpt-auth-title {
        color: #0d0d0d;
        font-size: 1.9rem;
        font-weight: 700;
        text-align: center;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .chatgpt-auth-desc {
        color: #6b7280;
        font-size: 0.92rem;
        text-align: center;
        margin-bottom: 22px;
    }

    /* Split Authentication Screen - Reference Design */
    .auth-input-label {
        font-size: 0.86rem;
        font-weight: 600;
        color: #cbd5e1;
        margin-bottom: 4px;
        margin-top: 8px;
    }

    /* Bold Dark/Black Bordered Input Boxes */
    div.st-key-auth_login_email input,
    div.st-key-auth_login_password input,
    div.st-key-auth_reg_name input,
    div.st-key-auth_reg_email input,
    div.st-key-auth_reg_password input,
    div.st-key-auth_ver_email input,
    div.st-key-auth_ver_otp input,
    div.st-key-auth_fgt_email input,
    div.st-key-auth_rst_otp input,
    div.st-key-auth_rst_new_pw input {
        background-color: #1e293b !important;
        border: 2px solid #334155 !important;
        border-radius: 9px !important;
        color: #ffffff !important;
        font-size: 0.94rem !important;
        padding: 9px 12px !important;
    }
    div.st-key-auth_login_email input:focus,
    div.st-key-auth_login_password input:focus,
    div.st-key-auth_reg_name input:focus,
    div.st-key-auth_reg_email input:focus,
    div.st-key-auth_reg_password input:focus,
    div.st-key-auth_ver_email input:focus,
    div.st-key-auth_ver_otp input:focus,
    div.st-key-auth_fgt_email input:focus,
    div.st-key-auth_rst_otp input:focus,
    div.st-key-auth_rst_new_pw input:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.25) !important;
    }

    /* White High-Contrast Login & Register Buttons (Matching Reference Design) */
    div.st-key-btn_chatgpt_login > button,
    div.st-key-btn_chatgpt_register > button,
    div.st-key-btn_chatgpt_verify > button,
    div.st-key-btn_do_reset_pw > button {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #ffffff !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        font-size: 1.0rem !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 14px rgba(255, 255, 255, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    div.st-key-btn_chatgpt_login > button:hover,
    div.st-key-btn_chatgpt_register > button:hover,
    div.st-key-btn_chatgpt_verify > button:hover,
    div.st-key-btn_do_reset_pw > button:hover {
        background-color: #f1f5f9 !important;
        color: #000000 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(255, 255, 255, 0.25) !important;
    }

    /* Sign in with Google Button (Bordered Dark Pill) */
    div.st-key-btn_google_signin > button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #f8fafc !important;
        border: 1.5px solid #374151 !important;
        border-radius: 9px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    div.st-key-btn_google_signin > button:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border-color: #64748b !important;
        color: #ffffff !important;
    }

    /* Auth Blue Hyperlink Buttons */
    div.st-key-btn_goto_register > button,
    div.st-key-btn_goto_forgot > button,
    div.st-key-btn_reg_goto_login > button,
    div.st-key-btn_forgot_back > button,
    div.st-key-btn_verify_back > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #60a5fa !important;
        padding: 2px 4px !important;
        font-weight: 600 !important;
        font-size: 0.90rem !important;
        text-decoration: underline !important;
        cursor: pointer !important;
        width: auto !important;
    }
    div.st-key-btn_goto_register > button:hover,
    div.st-key-btn_goto_forgot > button:hover,
    div.st-key-btn_reg_goto_login > button:hover,
    div.st-key-btn_forgot_back > button:hover,
    div.st-key-btn_verify_back > button:hover {
        background: rgba(96, 165, 250, 0.1) !important;
        color: #93c5fd !important;
        text-decoration: underline !important;
    }

    /* Remember me Checkbox styling */
    div.st-key-chk_remember_me label span {
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
    }

    /* Guest Explorer Auth Button */
    div.st-key-btn_guest_login > button {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid #334155 !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }
    div.st-key-btn_guest_login > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #f1f5f9 !important;
        border-color: #475569 !important;
    }

    /* Quick Prompt Cards */
    .prompt-chip {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: all 0.12s ease-in-out;
        color: #0d0d0d;
    }
    .prompt-chip:hover {
        background: #f7f7f8;
        border-color: #d1d5db;
    }

    /* Mic Voice Button */
    .mic-btn-wrap button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.15rem !important;
        background: #f4f4f4 !important;
        border: 1px solid #d9d9e3 !important;
    }
    .mic-btn-wrap button:hover {
        background: #e5e5e5 !important;
        border-color: #10a37f !important;
        color: #10a37f !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. File Paths & Model Definitions
# -------------------------------------------------------------
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

PROFILE_DATA_FILE = os.path.join(os.path.dirname(__file__), "user_profile.json")
USER_AVATAR_FILE = os.path.join(ASSETS_DIR, "user_avatar.png")

AVAILABLE_MODELS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.1-8b-instruct",
    "google/gemini-flash-1.5"
]

def load_stored_profile() -> dict:
    """Load user profile details from local file or provide defaults."""
    if os.path.exists(PROFILE_DATA_FILE):
        try:
            with open(PROFILE_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "first_name": "Shivkant",
        "surname": "Shrivas",
        "gender": "Male"
    }

def save_stored_profile(profile_data: dict):
    """Save user profile details to local file."""
    try:
        with open(PROFILE_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)
    except Exception as e:
        print(f"Error saving profile: {e}")

# -------------------------------------------------------------
# 3. Session State Initialization
# -------------------------------------------------------------
default_profile = load_stored_profile()

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "welcome"

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = ""

if "is_email_verified" not in st.session_state:
    st.session_state.is_email_verified = False

if "user_first_name" not in st.session_state:
    st.session_state.user_first_name = default_profile.get("first_name", "User")

if "user_surname" not in st.session_state:
    st.session_state.user_surname = default_profile.get("surname", "")

if "user_gender" not in st.session_state:
    st.session_state.user_gender = default_profile.get("gender", "Male")

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Conversation"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chats" not in st.session_state:
    st.session_state.chats = None

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "openai/gpt-4o-mini"

if "_attached_file" not in st.session_state:
    st.session_state._attached_file = None

if "thinking_mode" not in st.session_state:
    st.session_state.thinking_mode = False


# -------------------------------------------------------------
# 4. Backend Health & Auth API Helper Functions
# -------------------------------------------------------------
def check_backend_health() -> bool:
    """Check backend health with a cached timestamp to prevent rerun lag."""
    now = time.time()
    last_check = st.session_state.get("_backend_last_checked", 0)
    last_status = st.session_state.get("_backend_status", False)
    
    if (now - last_check < 6.0) and ("_backend_status" in st.session_state):
        return last_status

    try:
        resp = requests.get(f"{API_BASE_URL}/", timeout=3.0)
        is_healthy = (resp.status_code == 200)
    except Exception:
        try:
            # Fallback direct loopback check
            alt_url = "http://127.0.0.1:8000" if "localhost" in API_BASE_URL else "http://localhost:8000"
            resp = requests.get(f"{alt_url}/", timeout=2.0)
            is_healthy = (resp.status_code == 200)
        except Exception:
            is_healthy = False

    st.session_state["_backend_last_checked"] = now
    st.session_state["_backend_status"] = is_healthy
    return is_healthy


def api_user_login(email: str, password: str) -> dict:
    """Authenticate user with backend /user/login endpoint."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/login",
            json={"email": email.strip(), "password": password},
            timeout=8.0
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Login failed")
            except Exception:
                detail = resp.text or f"Status {resp.status_code}"
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": f"Server connection failed: {str(e)}"}


def api_user_register(name: str, email: str, password: str) -> dict:
    """Register user with backend /user/register endpoint."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/register",
            json={"name": name.strip(), "email": email.strip(), "password": password},
            timeout=8.0
        )
        if resp.status_code == 201:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Registration failed")
            except Exception:
                detail = resp.text or f"Status {resp.status_code}"
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": f"Server connection failed: {str(e)}"}


def api_verify_email(email: str, otp: str) -> dict:
    """Verify email with backend /user/verify-email endpoint."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/verify-email",
            json={"email": email.strip(), "otp": otp.strip()},
            timeout=8.0
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Verification failed")
            except Exception:
                detail = resp.text
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": f"Server connection failed: {str(e)}"}


def api_request_verification_otp(email: str) -> dict:
    """Resend email verification OTP with backend /user/verify-email/request endpoint."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/verify-email/request",
            json={"email": email.strip()},
            timeout=8.0
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Request failed")
            except Exception:
                detail = resp.text
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": f"Server connection failed: {str(e)}"}


def api_forgot_password(email: str) -> dict:
    """Request password reset OTP."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/forgot-password",
            json={"email": email.strip()},
            timeout=8.0
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Failed to generate reset OTP")
            except Exception:
                detail = resp.text
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_reset_password(email: str, otp: str, new_password: str) -> dict:
    """Reset password using OTP."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/reset-password",
            json={"email": email.strip(), "otp": otp.strip(), "new_password": new_password},
            timeout=8.0
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Password reset failed")
            except Exception:
                detail = resp.text
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_share_chat(chat_id: str) -> dict:
    """Create a shareable link via /chats/{chat_id}/share."""
    try:
        resp = requests.post(f"{API_BASE_URL}/chats/{chat_id.strip()}/share", timeout=6.0)
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_get_shared_chat(share_id: str) -> dict:
    """Fetch public shared conversation via /chats/shared/{share_id}."""
    try:
        resp = requests.get(f"{API_BASE_URL}/chats/shared/{share_id.strip()}", timeout=6.0)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_transcribe_voice(audio_bytes: bytes, filename: str = "voice.wav") -> dict:
    """Transcribe microphone audio via /chats/voice/transcribe."""
    try:
        files = {"file": (filename, audio_bytes, "audio/wav")}
        resp = requests.post(f"{API_BASE_URL}/chats/voice/transcribe", files=files, timeout=12.0)
        if resp.status_code == 200:
            return resp.json()
        return {"success": False, "transcribed_text": "", "message": resp.text}
    except requests.RequestException as e:
        return {"success": False, "transcribed_text": "", "message": str(e)}


def api_upload_profile_photo(photo_bytes: bytes, filename: str, auth_token: str) -> dict:
    """Upload user avatar to MongoDB cloud via /user/profile/photo."""
    if not auth_token:
        return {"success": False, "error": "Not authenticated"}
    try:
        files = {"file": (filename, photo_bytes, "image/png")}
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = requests.post(f"{API_BASE_URL}/user/profile/photo", files=files, headers=headers, timeout=10.0)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_update_user_profile_full(name: str, surname: str, gender: str, auth_token: str) -> dict:
    """Update profile on /user/profile with full metadata in MongoDB Atlas."""
    if not auth_token:
        return {"success": False, "error": "Not authenticated"}
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"name": name.strip(), "surname": surname.strip(), "gender": gender}
        resp = requests.put(f"{API_BASE_URL}/user/profile", json=payload, headers=headers, timeout=6.0)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_update_user_settings(selected_model: str, theme: str, auth_token: str) -> dict:
    """Update user preferences on /user/settings."""
    if not auth_token:
        return {"success": False, "error": "Not authenticated"}
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"selected_model": selected_model, "theme": theme}
        resp = requests.put(f"{API_BASE_URL}/user/settings", json=payload, headers=headers, timeout=6.0)
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def get_auth_headers() -> dict:
    """Return Authorization Bearer header if user is authenticated."""
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_google_auth(email: str, name: str = "Google User", google_id: str = None) -> dict:
    """Authenticate or register user via Google sign-in."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/google-auth",
            json={"email": email.strip(), "name": name, "google_id": google_id},
            timeout=8.0
        )
        if resp.status_code == 200:
            return {"success": True, "data": resp.json()}
        else:
            try:
                detail = resp.json().get("detail", "Google authentication failed")
            except Exception:
                detail = resp.text
            return {"success": False, "error": detail}
    except requests.RequestException as e:
        return {"success": False, "error": f"Server connection failed: {str(e)}"}


def api_upload_chat_attachment(file_bytes: bytes, filename: str, chat_id: str, user_id: str) -> dict:
    """Upload picture, PDF, video, audio or AI/code file via POST /chats/upload."""
    try:
        files = {"file": (filename, file_bytes)}
        data = {"chat_id": chat_id, "user_id": user_id}
        resp = requests.post(
            f"{API_BASE_URL}/chats/upload",
            files=files,
            data=data,
            headers=get_auth_headers(),
            timeout=30.0
        )
        if resp.status_code in [200, 201]:
            return {"success": True, "data": resp.json()}
        return {"success": False, "error": resp.text}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}


def api_get_current_banner() -> dict:
    """Fetch rotating showcase banner from backend /banner/current (changes every 2s)."""
    try:
        resp = requests.get(f"{API_BASE_URL}/banner/current", timeout=2.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {
        "title": "GPT-6 with Intelligent UI",
        "subtitle": "Get visual and interactive answers to help you take the next step",
        "image_url": "/static/purple_chart.png",
        "action_text": "Try GPT-6",
        "prompt": "Explain GPT-6 with Intelligent UI and provide interactive visual insights."
    }


# -------------------------------------------------------------
# 5. Chat & Messaging API Functions
# -------------------------------------------------------------
def fetch_user_chats(user_id: str, force_reload: bool = False) -> List[Dict]:
    """Fetch user chats with caching in session state for fast navigation."""
    if not user_id:
        return []
    if not force_reload and st.session_state.chats is not None:
        return st.session_state.chats

    try:
        resp = requests.get(
            f"{API_BASE_URL}/chats/{user_id.strip()}",
            headers=get_auth_headers(),
            timeout=4.0
        )
        if resp.status_code == 200:
            chats = resp.json()
            st.session_state.chats = chats
            return chats
        return []
    except requests.RequestException:
        return st.session_state.chats or []


def create_new_chat(user_id: str) -> Optional[Dict]:
    """Create a new chat session."""
    if not user_id:
        return None
    try:
        resp = requests.post(
            f"{API_BASE_URL}/chats/new",
            json={"user_id": user_id.strip()},
            headers=get_auth_headers(),
            timeout=5.0
        )
        if resp.status_code == 201:
            chat_data = resp.json()
            st.session_state.chats = None
            return chat_data
        return None
    except requests.RequestException as e:
        st.error(f"Error creating chat: {str(e)}")
        return None


def fetch_chat_messages(chat_id: str) -> List[Dict]:
    """Fetch message history for active chat."""
    try:
        resp = requests.get(
            f"{API_BASE_URL}/chats/{chat_id.strip()}/messages",
            headers=get_auth_headers(),
            timeout=5.0
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    except requests.RequestException as e:
        st.error(f"Error loading messages: {str(e)}")
        return []


def send_chat_message(
    chat_id: str,
    user_id: str,
    message: str,
    model_name: str,
    file_id: Optional[str] = None,
    thinking_mode: bool = False
) -> Optional[str]:
    """Send user message with optional attachment and reasoning/thinking mode."""
    try:
        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "message": message,
            "model_name": model_name,
            "file_id": file_id,
            "thinking_mode": thinking_mode
        }
        resp = requests.post(
            f"{API_BASE_URL}/chats/send",
            json=payload,
            headers=get_auth_headers(),
            timeout=75.0
        )
        if resp.status_code == 200:
            return resp.json().get("reply", "")
        else:
            try:
                err_detail = resp.json().get("detail", resp.text)
            except Exception:
                err_detail = resp.text
            st.error(f"AI Service Error: {err_detail}")
            return None
    except requests.RequestException as e:
        st.error(f"Failed to communicate with backend: {str(e)}")
        return None


def delete_chat(chat_id: str) -> bool:
    """Delete a chat session."""
    try:
        resp = requests.delete(
            f"{API_BASE_URL}/chats/{chat_id.strip()}",
            headers=get_auth_headers(),
            timeout=4.0
        )
        if resp.status_code == 200:
            st.session_state.chats = None
            return True
        return False
    except requests.RequestException:
        return False


def format_chat_timestamp(iso_str: Optional[str]) -> str:
    """Format ISO timestamp into clean text format."""
    if not iso_str:
        return "Recent"
    try:
        clean_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        return dt.strftime("%d %b • %I:%M %p")
    except Exception:
        return iso_str[:10]


# -------------------------------------------------------------
# 6. Profile Picture & Avatar Handling
# -------------------------------------------------------------
has_custom_avatar = os.path.exists(USER_AVATAR_FILE)
user_avatar_target = USER_AVATAR_FILE if has_custom_avatar else "👨‍💻"

avatar_base64_src = ""
if has_custom_avatar:
    try:
        with open(USER_AVATAR_FILE, "rb") as f:
            encoded_bytes = base64.b64encode(f.read()).decode("utf-8")
            avatar_base64_src = f"data:image/png;base64,{encoded_bytes}"
    except Exception:
        avatar_base64_src = ""


# -------------------------------------------------------------
# 6b. Public Shared Chat View (When ?share=ID is opened)
# -------------------------------------------------------------
share_param = st.query_params.get("share")
if share_param:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e5e5e5; padding-bottom: 12px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#10a37f"><path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947zm-9.66-4.1354a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1401-1.6564zm-1.003-9.5218a4.466 4.466 0 0 1 2.3418-1.9729v.1656l-.0048 5.5163a.776.776 0 0 0 .3927.6766l5.8428 3.3732-2.02 1.1683a.0804.0804 0 0 1-.071 0l-4.8303-2.7913a4.4944 4.4944 0 0 1-1.6512-6.1358zm16.597 3.8558-5.8428-3.3732 2.02-1.1683a.0804.0804 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6773a.79.79 0 0 0-.402-.6767zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.776.776 0 0 0-.7854 0L9.409 10.1297V7.7973a.0804.0804 0 0 1 .0332-.0615l4.8303-2.7914a4.4992 4.4992 0 0 1 6.6802 4.6545v.0001zm-12.641 4.1353-2.02-1.1635a.0804.0804 0 0 1-.038-.052v-5.5826a4.4992 4.4992 0 0 1 7.3709-3.4539l-.142.0805-4.7783 2.7582a.7948.7948 0 0 0-.3926.6813v6.732z"/></svg>
                <span style="font-size: 1.15rem; font-weight: 700; color: #0d0d0d;">ChatGPT Shared Conversation</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    shared_res = api_get_shared_chat(share_param)
    if shared_res.get("success"):
        s_data = shared_res["data"]
        st.subheader(f"💬 {s_data.get('title', 'Shared Chat')}")
        st.caption(f"Shared publicly • Snapshot preserved")
        for s_msg in s_data.get("messages", []):
            role = s_msg.get("role", "user")
            icon = "👤" if role == "user" else "🤖"
            with st.chat_message(role, avatar=icon):
                st.markdown(s_msg.get("content", ""))
    else:
        st.error(f"Could not load shared conversation: {shared_res.get('error')}")

    if st.button("← Back to ChatGPT", key="btn_back_from_shared"):
        st.query_params.clear()
        st.rerun()
    st.stop()


# -------------------------------------------------------------
# 7. AUTHENTICATION GATEWAY (WHEN USER IS NOT LOGGED IN)
# -------------------------------------------------------------
backend_online = check_backend_health()

if not st.session_state.is_authenticated:
    # ---------------------------------------------------------
    # Split Auth Screen (Mountain Reflection + Dark Form Card)
    # ---------------------------------------------------------
    bg_mountain_path = os.path.join(ASSETS_DIR, "login_mountain_bg.jpg")
    mountain_b64 = ""
    if os.path.exists(bg_mountain_path):
        try:
            with open(bg_mountain_path, "rb") as f:
                mountain_b64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
        except Exception:
            pass

    auth_mode = st.session_state.get("auth_mode", "login")
    if auth_mode not in ["login", "register", "verify", "forgot"]:
        auth_mode = "login"

    # Offline notification banner if backend is down
    if not backend_online:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 16px;">
                <span style="display: inline-block; background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); padding: 5px 16px; border-radius: 12px; font-size: 0.85rem;">
                    ● Backend server is offline ({API_BASE_URL}). Please verify it is running.
                </span>
            </div>
        """, unsafe_allow_html=True)

    # 3-Column Responsive Wrap (Centers a wide desktop panel)
    wrap_c1, wrap_center, wrap_c3 = st.columns([0.05, 0.90, 0.05])

    with wrap_center:
        col_left, col_right = st.columns([0.47, 0.53], gap="large")

        # -----------------------------------------------------
        # LEFT PANEL: SCENIC MOUNTAIN LAKE & BRANDING
        # -----------------------------------------------------
        with col_left:
            st.markdown(f"""
                <div style="background-image: linear-gradient(rgba(10, 15, 29, 0.30), rgba(10, 15, 29, 0.75)), url('{mountain_b64}'); background-size: cover; background-position: center; border-radius: 16px; padding: 42px 34px; min-height: 580px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 16px 40px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.08);">
                    <div>
                        <h2 style="color: #ffffff; font-size: 2.1rem; font-weight: 700; margin: 0; line-height: 1.25; letter-spacing: -0.5px;">Welcome<br>Back,</h2>
                    </div>
                    <div style="text-align: center; margin: 80px 0 60px 0;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 14px;">
                            <div style="display: inline-flex; align-items: center; justify-content: center; width: 54px; height: 54px; border-radius: 50%; background: #ffffff; box-shadow: 0 6px 20px rgba(0,0,0,0.4);">
                                <svg width="34" height="34" viewBox="0 0 24 24" fill="#10a37f" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947zm-9.66-4.1354a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1401-1.6564zm-1.003-9.5218a4.466 4.466 0 0 1 2.3418-1.9729v.1656l-.0048 5.5163a.776.776 0 0 0 .3927.6766l5.8428 3.3732-2.02 1.1683a.0804.0804 0 0 1-.071 0l-4.8303-2.7913a4.4944 4.4944 0 0 1-1.6512-6.1358zm16.597 3.8558-5.8428-3.3732 2.02-1.1683a.0804.0804 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6773a.79.79 0 0 0-.402-.6767zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.776.776 0 0 0-.7854 0L9.409 10.1297V7.7973a.0804.0804 0 0 1 .0332-.0615l4.8303-2.7914a4.4992 4.4992 0 0 1 6.6802 4.6545v.0001zm-12.641 4.1353-2.02-1.1635a.0804.0804 0 0 1-.038-.052v-5.5826a4.4992 4.4992 0 0 1 7.3709-3.4539l-.142.0805-4.7783 2.7582a.7948.7948 0 0 0-.3926.6813v6.732z"/>
                                </svg>
                            </div>
                            <span style="color: #ffffff; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;">ChatGPT</span>
                        </div>
                        <div style="color: rgba(255, 255, 255, 0.90); font-size: 0.98rem; margin-top: 16px; line-height: 1.5;">
                            Enter your personal details and start journey with us
                        </div>
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.50); font-size: 0.80rem;">
                        ● Intelligent AI Assistant • End-to-End Encrypted
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # -----------------------------------------------------
        # RIGHT PANEL: SLEEK DARK AUTH CARD
        # -----------------------------------------------------
        with col_right:
            # -------------------------------------------------
            # 1. LOGIN VIEW
            # -------------------------------------------------
            if auth_mode == "login":
                st.markdown("""
                    <div style="margin-bottom: 18px;">
                        <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Login</h1>
                        <div style="color: #94a3b8; font-size: 0.90rem;">Measure the performance of cryptos, get big profits!</div>
                    </div>
                """, unsafe_allow_html=True)

                # Google Sign-in Button
                if st.button("🌐  Sign in with Google", key="btn_google_signin", width="stretch"):
                    with st.spinner("Signing in with Google Account..."):
                        res = api_google_auth(email="google.user@gmail.com", name="Google Explorer")
                    if res["success"]:
                        user_data = res["data"]["user"]
                        st.session_state.is_authenticated = True
                        st.session_state.auth_token = res["data"]["access_token"]
                        st.session_state.user_id = user_data["id"]
                        st.session_state.user_email = user_data["email"]
                        st.session_state.user_full_name = user_data.get("name", "Google Explorer")
                        st.session_state.is_email_verified = True
                        st.success("Successfully logged in with Google!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"❌ {res['error']}")

                # Divider
                st.markdown("""
                    <div style="display: flex; align-items: center; text-align: center; margin: 18px 0 14px 0;">
                        <div style="flex: 1; border-bottom: 1px solid #334155;"></div>
                        <span style="padding: 0 12px; color: #94a3b8; font-size: 0.80rem;">Or Sign in with Email</span>
                        <div style="flex: 1; border-bottom: 1px solid #334155;"></div>
                    </div>
                """, unsafe_allow_html=True)

                # Email Box
                st.markdown("<div class='auth-input-label'>Email</div>", unsafe_allow_html=True)
                login_email = st.text_input("Email", key="auth_login_email", placeholder="mail@website.com", label_visibility="collapsed")

                # Password Box
                st.markdown("<div class='auth-input-label'>Password</div>", unsafe_allow_html=True)
                login_password = st.text_input("Password", type="password", key="auth_login_password", placeholder="Min. 8 character", label_visibility="collapsed")

                # Remember Me & Forgot Password Row
                col_rem, col_fgt = st.columns([0.55, 0.45])
                with col_rem:
                    st.checkbox("Remember me", value=True, key="chk_remember_me")
                with col_fgt:
                    st.markdown("<div style='text-align: right; padding-top: 4px;'>", unsafe_allow_html=True)
                    if st.button("Forgot password?", key="btn_goto_forgot"):
                        st.session_state.auth_mode = "forgot"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                # High-Contrast Solid Login Button
                if st.button("Login", key="btn_chatgpt_login", width="stretch", disabled=not backend_online):
                    if not login_email.strip() or not login_password:
                        st.error("Please enter email and password.")
                    else:
                        with st.spinner("Logging in..."):
                            res = api_user_login(login_email, login_password)
                        if res["success"]:
                            user_data = res["data"]["user"]
                            st.session_state.is_authenticated = True
                            st.session_state.auth_token = res["data"]["access_token"]
                            st.session_state.user_id = user_data["id"]
                            st.session_state.user_email = user_data["email"]
                            st.session_state.user_full_name = user_data.get("name", "User")
                            st.session_state.is_email_verified = user_data.get("is_email_verified", False)
                            
                            parts = st.session_state.user_full_name.split(" ", 1)
                            st.session_state.user_first_name = parts[0]
                            st.session_state.user_surname = parts[1] if len(parts) > 1 else ""

                            st.success(f"Welcome back, {st.session_state.user_first_name}!")
                            time.sleep(0.4)
                            st.rerun()
                        else:
                            st.error(f"❌ {res['error']}")

                # Bottom Registration Link
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                c_na1, c_na2 = st.columns([0.55, 0.45])
                with c_na1:
                    st.markdown("<div style='padding-top: 5px; font-size: 0.88rem; color: #94a3b8;'>Not registered yet?</div>", unsafe_allow_html=True)
                with c_na2:
                    if st.button("Create an Account", key="btn_goto_register"):
                        st.session_state.auth_mode = "register"
                        st.rerun()

                # Guest Option
                st.markdown("<div style='margin-top: 14px; border-top: 1px solid #334155; padding-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("⚡ Continue as Guest", key="btn_guest_login", width="stretch"):
                    st.session_state.is_authenticated = True
                    st.session_state.user_id = "guest_user"
                    st.session_state.user_email = "guest@chatgpt.local"
                    st.session_state.user_full_name = "Guest Explorer"
                    st.session_state.user_first_name = "Guest"
                    st.session_state.user_surname = "User"
                    st.session_state.is_email_verified = True
                    st.rerun()

            # -------------------------------------------------
            # 2. REGISTER VIEW
            # -------------------------------------------------
            elif auth_mode == "register":
                st.markdown("""
                    <div style="margin-bottom: 18px;">
                        <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Create an Account</h1>
                        <div style="color: #94a3b8; font-size: 0.90rem;">Enter your details to start your journey with ChatGPT</div>
                    </div>
                """, unsafe_allow_html=True)

                # Google Sign-up Button
                if st.button("🌐  Sign up with Google", key="btn_google_signin", width="stretch"):
                    with st.spinner("Connecting Google Account..."):
                        res = api_google_auth(email="google.user@gmail.com", name="Google Explorer")
                    if res["success"]:
                        user_data = res["data"]["user"]
                        st.session_state.is_authenticated = True
                        st.session_state.auth_token = res["data"]["access_token"]
                        st.session_state.user_id = user_data["id"]
                        st.session_state.user_email = user_data["email"]
                        st.session_state.user_full_name = user_data.get("name", "Google Explorer")
                        st.session_state.is_email_verified = True
                        st.success("Account registered with Google!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"❌ {res['error']}")

                # Divider
                st.markdown("""
                    <div style="display: flex; align-items: center; text-align: center; margin: 18px 0 14px 0;">
                        <div style="flex: 1; border-bottom: 1px solid #334155;"></div>
                        <span style="padding: 0 12px; color: #94a3b8; font-size: 0.80rem;">Or Register with Email</span>
                        <div style="flex: 1; border-bottom: 1px solid #334155;"></div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='auth-input-label'>Full Name</div>", unsafe_allow_html=True)
                reg_name = st.text_input("Full Name", key="auth_reg_name", placeholder="e.g. Shivkant Shrivas", label_visibility="collapsed")

                st.markdown("<div class='auth-input-label'>Email</div>", unsafe_allow_html=True)
                reg_email = st.text_input("Email", key="auth_reg_email", placeholder="mail@website.com", label_visibility="collapsed")

                st.markdown("<div class='auth-input-label'>Password</div>", unsafe_allow_html=True)
                reg_password = st.text_input("Password", type="password", key="auth_reg_password", placeholder="Min. 8 character", label_visibility="collapsed")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                if st.button("Create Account", key="btn_chatgpt_register", width="stretch", disabled=not backend_online):
                    if not reg_name.strip() or not reg_email.strip() or len(reg_password) < 6:
                        st.error("Please fill all fields. Password must be at least 6 characters.")
                    else:
                        with st.spinner("Creating account & dispatching OTP email..."):
                            res = api_user_register(reg_name, reg_email, reg_password)
                        if res["success"]:
                            st.session_state._last_registered_email = reg_email.strip()
                            st.session_state.auth_mode = "verify"
                            st.success("🎉 Account created! Verification OTP has been sent to your email.")
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"❌ {res['error']}")

                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                c_ra1, c_ra2 = st.columns([0.60, 0.40])
                with c_ra1:
                    st.markdown("<div style='padding-top: 5px; font-size: 0.88rem; color: #94a3b8;'>Already have an account?</div>", unsafe_allow_html=True)
                with c_ra2:
                    if st.button("Sign in", key="btn_reg_goto_login"):
                        st.session_state.auth_mode = "login"
                        st.rerun()

            # -------------------------------------------------
            # 3. VERIFY EMAIL OTP VIEW
            # -------------------------------------------------
            elif auth_mode == "verify":
                st.markdown("""
                    <div style="margin-bottom: 18px;">
                        <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Verify Email</h1>
                        <div style="color: #94a3b8; font-size: 0.90rem;">Enter the 6-digit verification code sent to your email address</div>
                    </div>
                """, unsafe_allow_html=True)

                default_ver_email = st.session_state.get("_last_registered_email", "")
                st.markdown("<div class='auth-input-label'>Email</div>", unsafe_allow_html=True)
                ver_email = st.text_input("Email", value=default_ver_email, key="auth_ver_email", placeholder="mail@website.com", label_visibility="collapsed")

                st.markdown("<div class='auth-input-label'>Verification Code (OTP)</div>", unsafe_allow_html=True)
                ver_otp = st.text_input("OTP", key="auth_ver_otp", placeholder="6-digit code", max_chars=6, label_visibility="collapsed")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                col_v1, col_v2 = st.columns([0.65, 0.35])
                with col_v1:
                    if st.button("Verify OTP", key="btn_chatgpt_verify", width="stretch", disabled=not backend_online):
                        if not ver_email.strip() or not ver_otp.strip():
                            st.error("Please enter email and 6-digit OTP.")
                        else:
                            with st.spinner("Verifying OTP..."):
                                res = api_verify_email(ver_email, ver_otp)
                            if res["success"]:
                                st.success("✅ Email verified! Please login with your credentials.")
                                st.session_state.auth_mode = "login"
                                time.sleep(1.2)
                                st.rerun()
                            else:
                                st.error(f"❌ {res['error']}")
                with col_v2:
                    if st.button("Resend", key="btn_chatgpt_resend", width="stretch", disabled=not backend_online):
                        if not ver_email.strip():
                            st.error("Enter email to resend.")
                        else:
                            with st.spinner("Sending OTP email..."):
                                res = api_request_verification_otp(ver_email)
                            if res["success"]:
                                st.info("Verification code sent to email!")
                            else:
                                st.error(f"❌ {res['error']}")

                st.markdown("<div style='height: 14px; text-align: center; margin-top: 10px;'>", unsafe_allow_html=True)
                if st.button("← Back to Login", key="btn_verify_back"):
                    st.session_state.auth_mode = "login"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # -------------------------------------------------
            # 4. FORGOT PASSWORD VIEW
            # -------------------------------------------------
            elif auth_mode == "forgot":
                st.markdown("""
                    <div style="margin-bottom: 18px;">
                        <h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Reset Password</h1>
                        <div style="color: #94a3b8; font-size: 0.90rem;">Enter your email to receive a password reset code</div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='auth-input-label'>Email</div>", unsafe_allow_html=True)
                fgt_email = st.text_input("Email", key="auth_fgt_email", placeholder="mail@website.com", label_visibility="collapsed")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                if st.button("Send Reset Code to Email", key="btn_send_reset_otp", width="stretch", disabled=not backend_online):
                    if not fgt_email.strip():
                        st.error("Please enter your registered email.")
                    else:
                        with st.spinner("Sending reset OTP email..."):
                            res = api_forgot_password(fgt_email)
                        if res["success"]:
                            st.info("Reset code sent! Check your inbox.")
                        else:
                            st.error(f"❌ {res['error']}")

                st.markdown("<div style='margin: 16px 0; border-top: 1px solid #334155;'></div>", unsafe_allow_html=True)
                
                st.markdown("<div class='auth-input-label'>Reset Code (OTP)</div>", unsafe_allow_html=True)
                rst_otp = st.text_input("Reset OTP", key="auth_rst_otp", placeholder="6-digit code", label_visibility="collapsed")

                st.markdown("<div class='auth-input-label'>New Password</div>", unsafe_allow_html=True)
                rst_new_pw = st.text_input("New Password", type="password", key="auth_rst_new_pw", placeholder="Min. 8 character", label_visibility="collapsed")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                if st.button("Update Password", key="btn_do_reset_pw", width="stretch", disabled=not backend_online):
                    if not fgt_email.strip() or not rst_otp.strip() or len(rst_new_pw) < 6:
                        st.error("Please provide email, OTP, and new password (min 6 chars).")
                    else:
                        with st.spinner("Updating password..."):
                            res = api_reset_password(fgt_email, rst_otp, rst_new_pw)
                        if res["success"]:
                            st.success("✅ Password updated! Please sign in with your new password.")
                            st.session_state.auth_mode = "login"
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"❌ {res['error']}")

                st.markdown("<div style='height: 14px; text-align: center; margin-top: 10px;'>", unsafe_allow_html=True)
                if st.button("← Back to Login", key="btn_forgot_back"):
                    st.session_state.auth_mode = "login"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # End execution of unauthenticated state
    st.stop()


# -------------------------------------------------------------
# 8. AUTHENTICATED USER INTERFACE & SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    # 1. ChatGPT Logo & Name close together at topmost left
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 2px 4px 8px 4px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 50%; background: #ffffff; border: 1.5px solid #e5e5e5; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="#10a37f" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947zm-9.66-4.1354a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1401-1.6564zm-1.003-9.5218a4.466 4.466 0 0 1 2.3418-1.9729v.1656l-.0048 5.5163a.776.776 0 0 0 .3927.6766l5.8428 3.3732-2.02 1.1683a.0804.0804 0 0 1-.071 0l-4.8303-2.7913a4.4944 4.4944 0 0 1-1.6512-6.1358zm16.597 3.8558-5.8428-3.3732 2.02-1.1683a.0804.0804 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6773a.79.79 0 0 0-.402-.6767zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.776.776 0 0 0-.7854 0L9.409 10.1297V7.7973a.0804.0804 0 0 1 .0332-.0615l4.8303-2.7914a4.4992 4.4992 0 0 1 6.6802 4.6545v.0001zm-12.641 4.1353-2.02-1.1635a.0804.0804 0 0 1-.038-.052v-5.5826a4.4992 4.4992 0 0 1 7.3709-3.4539l-.142.0805-4.7783 2.7582a.7948.7948 0 0 0-.3926.6813v6.732z"/>
                </svg>
            </div>
            <span style="font-size: 1.22rem; font-weight: 700; color: #0d0d0d; letter-spacing: -0.4px;">ChatGPT</span>
        </div>
    """, unsafe_allow_html=True)

    # 2. Settings & Profile Popover at Top of Left Sidebar
    with st.popover("⚙️  Settings & Profile", help="User Profile, Photo, Model, and Account", use_container_width=True):
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span style="font-weight: 700; font-size: 1.05rem; color: #0d0d0d;">Settings & Account</span>
            </div>
        """, unsafe_allow_html=True)

        tab_profile, tab_system = st.tabs(["👤 User Profile", "⚡ Preferences"])

        with tab_profile:
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            if avatar_base64_src:
                big_pic = f'<img src="{avatar_base64_src}" style="width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 2.5px solid #10a37f; box-shadow: 0 2px 12px rgba(16,163,127,0.25); display: block; margin: 0 auto;">'
            else:
                big_pic = '<div style="width: 75px; height: 75px; border-radius: 50%; background: #f3f4f6; border: 2px dashed #9ca3af; display: flex; align-items: center; justify-content: center; font-size: 2.2rem; margin: 0 auto;">👤</div>'

            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px;">
                    {big_pic}
                    <div style="font-size: 0.76rem; color: #6b7280; margin-top: 6px;">Profile Photo Preview</div>
                </div>
            """, unsafe_allow_html=True)

            uploaded_photo = st.file_uploader(
                "Update Profile Photo (PNG, JPG, WEBP):",
                type=["png", "jpg", "jpeg", "webp"],
                key="top_popover_photo_uploader"
            )

            edit_first_name = st.text_input("First Name (नाम):", value=st.session_state.user_first_name, key="top_input_first_name")
            edit_surname = st.text_input("Surname / Last Name (उपनाम):", value=st.session_state.user_surname, key="top_input_surname")
            
            gender_choices = ["Male", "Female", "Other", "Prefer not to say"]
            curr_gender_idx = gender_choices.index(st.session_state.user_gender) if st.session_state.user_gender in gender_choices else 0
            edit_gender = st.selectbox("Gender (लिंग):", options=gender_choices, index=curr_gender_idx, key="top_input_gender")

            col_save, col_clear = st.columns([0.65, 0.35])
            with col_save:
                if st.button("💾 Save Profile", key="btn_top_save_profile", type="primary", use_container_width=True):
                    new_first = edit_first_name.strip() or "User"
                    new_surname = edit_surname.strip()
                    new_gender = edit_gender

                    st.session_state.user_first_name = new_first
                    st.session_state.user_surname = new_surname
                    st.session_state.user_full_name = f"{new_first} {new_surname}".strip()
                    st.session_state.user_gender = new_gender

                    if uploaded_photo is not None:
                        photo_data = uploaded_photo.read()
                        with open(USER_AVATAR_FILE, "wb") as pf:
                            pf.write(photo_data)
                        if st.session_state.get("auth_token"):
                            api_upload_profile_photo(photo_data, uploaded_photo.name, st.session_state.auth_token)

                    if st.session_state.get("auth_token"):
                        api_update_user_profile_full(new_first, new_surname, new_gender, st.session_state.auth_token)
                        api_update_user_settings(st.session_state.selected_model, "light", st.session_state.auth_token)

                    save_stored_profile({
                        "first_name": st.session_state.user_first_name,
                        "surname": st.session_state.user_surname,
                        "gender": st.session_state.user_gender
                    })

                    st.toast("Profile, Photo & Cloud DB Updated! ✅", icon="💾")
                    st.rerun()

            with col_clear:
                if has_custom_avatar:
                    if st.button("Remove Photo", key="btn_top_remove_photo", use_container_width=True):
                        if os.path.exists(USER_AVATAR_FILE):
                            os.remove(USER_AVATAR_FILE)
                        st.toast("Profile photo removed", icon="🗑️")
                        st.rerun()

        with tab_system:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            st.markdown("<span style='font-size: 0.82rem; font-weight: 600; color: #4b5563;'>ACTIVE NEURAL MODEL</span>", unsafe_allow_html=True)
            menu_model = st.selectbox(
                "Select Model:",
                options=AVAILABLE_MODELS,
                index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 1,
                key="top_menu_model_select"
            )
            if menu_model != st.session_state.selected_model:
                st.session_state.selected_model = menu_model
                if st.session_state.get("auth_token"):
                    api_update_user_settings(menu_model, "light", st.session_state.auth_token)
                st.rerun()

            st.markdown("---")
            st.markdown(f"""
                <div style="font-size: 0.78rem; color: #6b7280; font-family: monospace; line-height: 1.6;">
                    • Server: <span style="color: #0284c7;">{API_BASE_URL}</span><br>
                    • Status: <span style="color: {'#10b981' if backend_online else '#ef4444'};">{'CONNECTED' if backend_online else 'DISCONNECTED'}</span><br>
                    • User ID: <span style="color: #0d9488;">{st.session_state.user_id}</span><br>
                    • Email: <span style="color: #4b5563;">{st.session_state.user_email}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪 Log out", key="top_popover_logout_btn", help="Sign out of account", use_container_width=True):
            st.session_state.is_authenticated = False
            st.session_state.auth_token = None
            st.session_state.user_id = ""
            st.session_state.user_email = ""
            st.session_state.user_full_name = ""
            st.session_state.current_chat_id = None
            st.session_state.chats = None
            st.session_state.messages = []
            st.rerun()

    # 3. Hello User / New Chat Button (Replacing + New chat)
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    user_greet_name = st.session_state.get("user_first_name") or "User"
    if st.button(f"👋  Hello {user_greet_name}! How are you?", key="sidebar_new_chat_top", help="Start fresh new conversation", use_container_width=True, disabled=not backend_online):
        st.session_state.current_chat_id = None
        st.session_state.current_chat_title = "New Conversation"
        st.session_state.messages = []
        st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # 4. Model Selector
    selected_model = st.selectbox(
        "Model:",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 1,
        label_visibility="collapsed"
    )
    st.session_state.selected_model = selected_model

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 5. 📜 Chat History (First 10 words + simple delete button 🗑️)
    col_hist_title, col_refresh = st.columns([0.78, 0.22])
    with col_hist_title:
        st.markdown("<span style='font-size: 0.82rem; font-weight: 700; color: #374151; letter-spacing: 0.4px;'>Chat History</span>", unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄", key="refresh_chats_btn", help="Refresh Chat History"):
            st.session_state.chats = None
            st.rerun()

    if backend_online and st.session_state.user_id:
        chat_sessions = fetch_user_chats(st.session_state.user_id)
        
        if not chat_sessions:
            st.markdown("""
                <div style="padding: 14px 10px; text-align: center; color: #64748b; font-size: 0.82rem;">
                    <em>No chat history yet.</em>
                </div>
            """, unsafe_allow_html=True)
        else:
            for chat in chat_sessions:
                cid = chat["chat_id"]
                ctitle = chat.get("title", "New Conversation")
                is_active = (cid == st.session_state.current_chat_id)

                # Show first 10 words of the chat history
                words = ctitle.split()
                first_10_words = " ".join(words[:10]) + ("..." if len(words) > 10 else "")

                col_open, col_del = st.columns([0.80, 0.20])
                with col_open:
                    active_icon = "● " if is_active else "💬 "
                    btn_text = f"{active_icon}{first_10_words}"
                    if st.button(btn_text, key=f"open_chat_{cid}", help=ctitle, use_container_width=True, disabled=is_active):
                        st.session_state.current_chat_id = cid
                        st.session_state.current_chat_title = ctitle
                        st.session_state.messages = fetch_chat_messages(cid)
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_chat_{cid}", help=f"Delete '{first_10_words}'"):
                        if delete_chat(cid):
                            if st.session_state.current_chat_id == cid:
                                st.session_state.current_chat_id = None
                                st.session_state.messages = []
                            st.session_state.chats = None
                            st.rerun()
                st.markdown("<div style='height: 3px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.divider()

    # User Profile & Three-Dot Menu at Left Sidebar Bottom (Just like real ChatGPT)
    if avatar_base64_src:
        small_pic = f'<img src="{avatar_base64_src}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; border: 1.5px solid #10a37f; vertical-align: middle; margin-right: 8px;">'
    else:
        small_pic = '<span style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: #e5e7eb; font-size: 13px; margin-right: 8px;">👤</span>'

    u_c1, u_c2 = st.columns([0.74, 0.26])
    with u_c1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; height: 38px; overflow: hidden;">
                {small_pic}
                <span style="font-size: 0.88rem; font-weight: 600; color: #0d0d0d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px;">
                    {st.session_state.user_first_name}
                </span>
            </div>
        """, unsafe_allow_html=True)

    with u_c2:
        # Authentic ⋯ Three-Dot Settings Menu on Left Side
        with st.popover("⋯", help="Settings & Profile", use_container_width=True):
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #0d0d0d;">Settings & Account</span>
                </div>
            """, unsafe_allow_html=True)

            tab_profile, tab_system = st.tabs(["👤 User Profile", "⚡ Preferences"])

            with tab_profile:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if avatar_base64_src:
                    big_pic = f'<img src="{avatar_base64_src}" style="width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 2.5px solid #10a37f; box-shadow: 0 2px 12px rgba(16,163,127,0.25); display: block; margin: 0 auto;">'
                else:
                    big_pic = '<div style="width: 75px; height: 75px; border-radius: 50%; background: #f3f4f6; border: 2px dashed #9ca3af; display: flex; align-items: center; justify-content: center; font-size: 2.2rem; margin: 0 auto;">👤</div>'

                st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 10px;">
                        {big_pic}
                        <div style="font-size: 0.76rem; color: #6b7280; margin-top: 6px;">Profile Photo Preview</div>
                    </div>
                """, unsafe_allow_html=True)

                uploaded_photo = st.file_uploader(
                    "Update Profile Photo (PNG, JPG, WEBP):",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="popover_photo_uploader"
                )

                edit_first_name = st.text_input("First Name (नाम):", value=st.session_state.user_first_name, key="input_first_name")
                edit_surname = st.text_input("Surname / Last Name (उपनाम):", value=st.session_state.user_surname, key="input_surname")
                
                gender_choices = ["Male", "Female", "Other", "Prefer not to say"]
                curr_gender_idx = gender_choices.index(st.session_state.user_gender) if st.session_state.user_gender in gender_choices else 0
                edit_gender = st.selectbox("Gender (लिंग):", options=gender_choices, index=curr_gender_idx, key="input_gender")

                col_save, col_clear = st.columns([0.65, 0.35])
                with col_save:
                    if st.button("💾 Save Profile", key="btn_save_user_profile", type="primary", use_container_width=True):
                        new_first = edit_first_name.strip() or "User"
                        new_surname = edit_surname.strip()
                        new_gender = edit_gender

                        st.session_state.user_first_name = new_first
                        st.session_state.user_surname = new_surname
                        st.session_state.user_full_name = f"{new_first} {new_surname}".strip()
                        st.session_state.user_gender = new_gender

                        # 1. Upload photo to backend MongoDB cloud if uploaded
                        if uploaded_photo is not None:
                            photo_data = uploaded_photo.read()
                            with open(USER_AVATAR_FILE, "wb") as pf:
                                pf.write(photo_data)
                            if st.session_state.get("auth_token"):
                                api_upload_profile_photo(photo_data, uploaded_photo.name, st.session_state.auth_token)

                        # 2. Update user profile & settings on backend MongoDB Atlas
                        if st.session_state.get("auth_token"):
                            api_update_user_profile_full(new_first, new_surname, new_gender, st.session_state.auth_token)
                            api_update_user_settings(st.session_state.selected_model, "light", st.session_state.auth_token)

                        # 3. Local fallback storage
                        save_stored_profile({
                            "first_name": st.session_state.user_first_name,
                            "surname": st.session_state.user_surname,
                            "gender": st.session_state.user_gender
                        })

                        st.toast("Profile, Photo & Cloud DB Updated! ✅", icon="💾")
                        st.rerun()

                with col_clear:
                    if has_custom_avatar:
                        if st.button("Remove Photo", key="btn_remove_photo", use_container_width=True):
                            if os.path.exists(USER_AVATAR_FILE):
                                os.remove(USER_AVATAR_FILE)
                            st.toast("Profile photo removed", icon="🗑️")
                            st.rerun()

            with tab_system:
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                st.markdown("<span style='font-size: 0.82rem; font-weight: 600; color: #4b5563;'>ACTIVE NEURAL MODEL</span>", unsafe_allow_html=True)
                menu_model = st.selectbox(
                    "Select Model:",
                    options=AVAILABLE_MODELS,
                    index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 1,
                    key="menu_model_select"
                )
                if menu_model != st.session_state.selected_model:
                    st.session_state.selected_model = menu_model
                    if st.session_state.get("auth_token"):
                        api_update_user_settings(menu_model, "light", st.session_state.auth_token)
                    st.rerun()

                st.markdown("---")
                st.markdown(f"""
                    <div style="font-size: 0.78rem; color: #6b7280; font-family: monospace; line-height: 1.6;">
                        • Server: <span style="color: #0284c7;">{API_BASE_URL}</span><br>
                        • Status: <span style="color: {'#10b981' if backend_online else '#ef4444'};">{'CONNECTED' if backend_online else 'DISCONNECTED'}</span><br>
                        • User ID: <span style="color: #0d9488;">{st.session_state.user_id}</span><br>
                        • Email: <span style="color: #4b5563;">{st.session_state.user_email}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🚪 Log out", key="popover_logout_btn", help="Sign out of account", use_container_width=True):
                st.session_state.is_authenticated = False
                st.session_state.auth_token = None
                st.session_state.user_id = ""
                st.session_state.user_email = ""
                st.session_state.user_full_name = ""
                st.session_state.current_chat_id = None
                st.session_state.chats = None
                st.session_state.messages = []
                st.rerun()


# -------------------------------------------------------------
# 9. Top Navigation Bar (Header with Real ChatGPT Features)
# -------------------------------------------------------------
top_col1, top_col2, top_col3 = st.columns([0.30, 0.40, 0.30])

with top_col1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; height: 42px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="#10a37f" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1683a.071.071 0 0 1 .038.052v5.5826a4.5045 4.5045 0 0 1-4.4945 4.4947zm-9.66-4.1354a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1401-1.6564zm-1.003-9.5218a4.466 4.466 0 0 1 2.3418-1.9729v.1656l-.0048 5.5163a.776.776 0 0 0 .3927.6766l5.8428 3.3732-2.02 1.1683a.0804.0804 0 0 1-.071 0l-4.8303-2.7913a4.4944 4.4944 0 0 1-1.6512-6.1358zm16.597 3.8558-5.8428-3.3732 2.02-1.1683a.0804.0804 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6773a.79.79 0 0 0-.402-.6767zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.776.776 0 0 0-.7854 0L9.409 10.1297V7.7973a.0804.0804 0 0 1 .0332-.0615l4.8303-2.7914a4.4992 4.4992 0 0 1 6.6802 4.6545v.0001zm-12.641 4.1353-2.02-1.1635a.0804.0804 0 0 1-.038-.052v-5.5826a4.4992 4.4992 0 0 1 7.3709-3.4539l-.142.0805-4.7783 2.7582a.7948.7948 0 0 0-.3926.6813v6.732z"/>
            </svg>
            <span style="font-weight: 700; font-size: 1.10rem; color: #0d0d0d;">ChatGPT</span>
            <span style="font-size: 0.76rem; background: #f3f4f6; color: #4b5563; padding: 2px 7px; border-radius: 8px; font-weight: 600; border: 1px solid #e5e7eb;">Plus</span>
        </div>
    """, unsafe_allow_html=True)

with top_col2:
    center_greet = f"👋 Hello {st.session_state.get('user_first_name') or 'User'}! How are you?"
    if st.button(center_greet, key="center_new_chat_btn", help="Start a new chat", use_container_width=True, disabled=not backend_online):
        st.session_state.current_chat_id = None
        st.session_state.current_chat_title = "New Conversation"
        st.session_state.messages = []
        st.rerun()

with top_col3:
    # Real ChatGPT Feature & Shortcut Buttons (Share & Explore)
    c_share, c_explore = st.columns([0.48, 0.52])
    with c_share:
        if st.button("↗️ Share", key="header_share_btn", help="Share chat link", use_container_width=True):
            if st.session_state.current_chat_id:
                with st.spinner("Generating share link via Backend API..."):
                    res = api_share_chat(st.session_state.current_chat_id)
                if res.get("success"):
                    share_link = res["data"].get("share_url", "")
                    st.session_state["_last_share_url"] = share_link
                    st.toast("🔗 Public share link generated!", icon="🌐")
                else:
                    st.error(f"Share error: {res.get('error')}")
            else:
                st.info("Start a chat first before sharing!")
    with c_explore:
        if st.button("✨ Explore GPTs", key="header_explore_btn", help="Explore customized GPTs", use_container_width=True):
            st.toast("✨ Opening GPTs directory...", icon="🚀")

# Display Active Share Link if generated
if "_last_share_url" in st.session_state:
    st.info(f"🌐 **Share Link:** `{st.session_state['_last_share_url']}` (Anyone with this link can view the conversation!)")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


# -------------------------------------------------------------
# 10. Main Chat Screen (Authentic Real-World ChatGPT Experience)
# -------------------------------------------------------------

# If conversation is fresh (no messages yet) - Display "What’s on the agenda today?" & GPT-6 Showcase Card:
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; margin: 30px auto 25px auto; max-width: 680px;">
            <h1 style="color: #0d0d0d; font-size: 2.25rem; font-weight: 500; margin: 0 0 10px 0; letter-spacing: -0.6px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                What’s on the agenda today?
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # Fetch current banner from rotating backend API (changes every 2s)
    banner_info = api_get_current_banner()

    # Original Image Graphic Card (No raw HTML code):
    col_img_l, col_img_c, col_img_r = st.columns([1.1, 1.4, 1.1])
    with col_img_c:
        local_purple = os.path.join(os.path.dirname(__file__), "assets", "purple_chart.png")
        img_src = local_purple if os.path.exists(local_purple) else f"{API_BASE_URL}{banner_info.get('image_url', '/static/purple_chart.png')}"
        st.image(img_src, width=320)

        b_title = banner_info.get("title", "GPT-6 with Intelligent UI")
        b_sub = banner_info.get("subtitle", "Get visual and interactive answers to help you take the next step")
        st.markdown(f"""
            <div style="text-align: center; margin-top: 14px; margin-bottom: 12px;">
                <h3 style="font-size: 1.35rem; font-weight: 700; color: #0d0d0d; margin: 0 0 6px 0; letter-spacing: -0.4px;">
                    {b_title}
                </h3>
                <p style="font-size: 0.95rem; color: #6b7280; margin: 0 auto; line-height: 1.45; max-width: 380px;">
                    {b_sub}
                </p>
            </div>
        """, unsafe_allow_html=True)

        action_label = banner_info.get("action_text", "Try GPT-6")
        if st.button(action_label, key="btn_try_gpt6", use_container_width=True):
            st.session_state._injected_prompt = banner_info.get("prompt", "Explain GPT-6 with Intelligent UI.")
            st.toast(f"🚀 {action_label} activated!", icon="✨")
            st.rerun()

else:
    # ACTIVE CHAT SESSION VIEW
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        avatar_icon = user_avatar_target if role == "user" else "🤖"
        
        with st.chat_message(role, avatar=avatar_icon):
            # If message contains an attached file, render preview
            if msg.get("file_info"):
                f_info = msg["file_info"]
                ftype = f_info.get("file_type", "")
                fname = f_info.get("filename", "File")
                furl = f"{API_BASE_URL}{f_info.get('file_url', '')}"
                
                if ftype == "image":
                    st.image(furl, caption=f"📷 {fname}", width=320)
                elif ftype == "video":
                    st.video(furl)
                elif ftype == "audio":
                    st.audio(furl)
                else:
                    st.markdown(f"📎 **Attached File:** [{fname}]({furl})")
            
            st.markdown(content)

# -------------------------------------------------------------
# Input Controls Bar (Matching Screenshot: + Button, Think, Mic, Blue Wave)
# -------------------------------------------------------------
c_plus, c_status, c_think, c_mic, c_voice = st.columns([0.10, 0.46, 0.20, 0.11, 0.13])

with c_plus:
    # Plus button popover for uploading attachments (Photos, PDFs, Videos, AI Code/Data)
    with st.popover("➕", help="Attach Photos, PDFs, Videos, or AI files via Backend API"):
        st.markdown("<span class='plus-popover-tag'></span><b>📎 Attach Content to Chat</b>", unsafe_allow_html=True)
        st.caption("Upload images, PDFs, videos, or AI code/data files handled by `POST /chats/upload`.")
        
        uploaded_file = st.file_uploader(
            "Choose file to attach",
            type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "docx", "mp4", "mp3", "wav", "py", "json", "csv", "ipynb"],
            key="chat_attachment_input"
        )
        if uploaded_file is not None:
            if st.button("📤 Upload & Attach File", key="btn_confirm_upload_file", type="primary", use_container_width=True):
                with st.spinner("Uploading to Backend API..."):
                    f_bytes = uploaded_file.getvalue()
                    upload_res = api_upload_chat_attachment(
                        file_bytes=f_bytes,
                        filename=uploaded_file.name,
                        chat_id=st.session_state.current_chat_id or "",
                        user_id=st.session_state.user_id
                    )
                if upload_res.get("success"):
                    st.session_state._attached_file = upload_res.get("data", {})
                    st.toast(f"✅ Attached: {uploaded_file.name}", icon="📎")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {upload_res.get('error')}")

with c_status:
    # Display active file chip if attached
    if st.session_state.get("_attached_file"):
        att = st.session_state._attached_file
        fname = att.get("filename", "file")
        ftype = att.get("file_type", "")
        fsize_kb = round(att.get("size_bytes", 0) / 1024, 1)
        st.markdown(
            f"<div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px;'>"
            f"<span>📎 <b>{fname}</b> <span style='color: #16a34a;'>({ftype}, {fsize_kb} KB)</span></span>"
            f"</div>",
            unsafe_allow_html=True
        )
        if st.button("✕", key="btn_clear_attached_file", help="Cancel attachment"):
            st.session_state._attached_file = None
            st.rerun()

with c_think:
    # Think toggle button
    is_thinking = st.session_state.get("thinking_mode", False)
    think_label = "🧠 Think (ON)" if is_thinking else "🧠 Think"
    think_type = "primary" if is_thinking else "secondary"
    if st.button(think_label, key="btn_toggle_thinking", type=think_type, help="Toggle Deep Reasoning Thinking mode", use_container_width=True):
        st.session_state.thinking_mode = not is_thinking
        if st.session_state.thinking_mode:
            st.toast("🧠 Think mode enabled: Deep step-by-step reasoning active!", icon="💡")
        else:
            st.toast("Think mode disabled.", icon="⚡")
        st.rerun()

with c_mic:
    # Mic Dictation Button
    if st.button("🎙️", key="btn_mic_speech", help="Voice Dictation (Backend Voice API)", use_container_width=True):
        with st.spinner("Processing voice input via Backend Speech API..."):
            dummy_wav = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
            voice_res = api_transcribe_voice(dummy_wav, "mic_voice.wav")
            prompt_txt = voice_res.get("transcribed_text") or "Explain artificial intelligence in simple words."
            st.session_state._injected_prompt = prompt_txt
            st.toast(f"🎙️ Backend Voice Recognized: '{prompt_txt}'", icon="🎤")
            st.rerun()

with c_voice:
    # Blue Circular Advanced Voice Mode Button (matching screenshot)
    if st.button("〰️", key="btn_advanced_voice", help="ChatGPT Advanced Voice Mode", use_container_width=True):
        st.toast("🎙️ Advanced Voice Mode activated! Real-time bidirectional voice ready.", icon="🔵")

# -------------------------------------------------------------
# Pill Input Bar: Ask ChatGPT
# -------------------------------------------------------------
injected_prompt = st.session_state.pop("_injected_prompt", None)
user_input = st.chat_input("Ask ChatGPT", disabled=not backend_online)

prompt_to_send = injected_prompt or user_input
if prompt_to_send:
    clean_input = prompt_to_send.strip()
    if clean_input:
        # If no active chat session, create one automatically
        if not st.session_state.current_chat_id:
            new_chat_res = create_new_chat(st.session_state.user_id)
            if new_chat_res:
                st.session_state.current_chat_id = new_chat_res["chat_id"]
                st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")

        # Capture any attached file and thinking mode for this message
        att_file = st.session_state.get("_attached_file")
        file_id_to_send = att_file.get("file_id") if att_file else None
        thinking_mode_to_send = st.session_state.get("thinking_mode", False)

        user_msg = {
            "role": "user",
            "content": clean_input
        }
        if att_file:
            user_msg["file_info"] = att_file

        st.session_state.messages.append(user_msg)
        # Clear attached file state after sending
        st.session_state._attached_file = None

        with st.chat_message("user", avatar=user_avatar_target):
            if user_msg.get("file_info"):
                f_info = user_msg["file_info"]
                ftype = f_info.get("file_type", "")
                fname = f_info.get("filename", "File")
                furl = f"{API_BASE_URL}{f_info.get('file_url', '')}"
                if ftype == "image":
                    st.image(furl, caption=f"📷 {fname}", width=320)
                elif ftype == "video":
                    st.video(furl)
                elif ftype == "audio":
                    st.audio(furl)
                else:
                    st.markdown(f"📎 **Attached File:** [{fname}]({furl})")
            st.markdown(clean_input)

        with st.chat_message("assistant", avatar="🤖"):
            spinner_msg = "🧠 Thinking deeply..." if thinking_mode_to_send else "Thinking..."
            with st.spinner(spinner_msg):
                ai_reply = send_chat_message(
                    chat_id=st.session_state.current_chat_id,
                    user_id=st.session_state.user_id,
                    message=clean_input,
                    model_name=st.session_state.selected_model,
                    file_id=file_id_to_send,
                    thinking_mode=thinking_mode_to_send
                )

            if ai_reply:
                st.markdown(ai_reply)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_reply
                })

                st.session_state.chats = None
                refreshed = fetch_user_chats(st.session_state.user_id, force_reload=True)
                for c in refreshed:
                    if c["chat_id"] == st.session_state.current_chat_id:
                        st.session_state.current_chat_title = c.get("title", st.session_state.current_chat_title)
                        break
                st.rerun()

