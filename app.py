import streamlit as st
import requests
import time
import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# -------------------------------------------------------------
# 1. Page Configuration & Futuristic Cyber Dark Theme
# -------------------------------------------------------------
st.set_page_config(
    page_title="NEXUS AI // Neural ChatBot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Cyberpunk Dark CSS (Zero flickering, snappy rendering)
st.markdown("""
<style>
    /* 1. Prevent Streamlit brightness fading/dimming during reruns */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #070a10 !important;
        background: radial-gradient(circle at 50% 0%, #0d1527 0%, #070a10 85%) !important;
        color: #e2e8f0 !important;
        opacity: 1 !important;
        transition: none !important;
    }
    
    div[data-testid="stAppViewContainer"] > section {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }

    div[data-st-app-view="true"], div[data-testid="stMain"], div[data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
        animation: none !important;
    }

    /* Hide the top-right blinking reload spinner indicator */
    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. Sidebar Cyber Dark Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid #162032 !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #00f2fe !important;
        letter-spacing: 0.5px;
    }

    /* 3. Tech Header Badge & Cards */
    .tech-header-card {
        background: linear-gradient(135deg, rgba(13, 21, 39, 0.9) 0%, rgba(9, 13, 23, 0.95) 100%);
        border: 1px solid #1e293b;
        border-left: 4px solid #00f2fe;
        border-radius: 12px;
        padding: 16px 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    
    .tech-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .tech-badge-cyan {
        display: inline-block;
        background: rgba(0, 242, 254, 0.12);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .tech-badge-green {
        display: inline-block;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .tech-badge-amber {
        display: inline-block;
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* 4. Chat History Item in Sidebar */
    .history-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        transition: all 0.15s ease-in-out;
    }
    
    .history-card:hover {
        background: rgba(30, 41, 59, 0.85);
        border-color: #00f2fe;
    }

    .history-card-active {
        background: rgba(0, 242, 254, 0.08) !important;
        border: 1px solid #00f2fe !important;
        box-shadow: 0 0 14px rgba(0, 242, 254, 0.15);
    }

    .history-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #f1f5f9;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }

    .history-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.70rem;
        color: #64748b;
        font-family: monospace;
    }

    /* 5. Custom Button Styling */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease-in-out !important;
    }

    /* Primary glowing action button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.25) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(0, 198, 255, 0.45) !important;
        transform: translateY(-1px);
    }

    /* Secondary outline button */
    div.stButton > button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid #334155 !important;
        color: #cbd5e1 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00f2fe !important;
        color: #ffffff !important;
    }

    /* Form and Input styling */
    div[data-baseweb="input"] {
        background-color: #0b0f19 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #00f2fe !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
    }

    /* Custom Chat Message Styling */
    div[data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
    }

    /* Model watermark inside chat bubble */
    .model-tag {
        font-size: 0.70rem;
        color: #64748b;
        font-family: monospace;
        margin-top: 8px;
        display: inline-block;
        background: rgba(15, 23, 42, 0.9);
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #1e293b;
    }

    /* Floating input container */
    .stChatFloatingInputContainer {
        bottom: 15px;
        background: transparent !important;
    }

    .auth-container {
        background: linear-gradient(135deg, rgba(13, 21, 39, 0.85) 0%, rgba(9, 13, 23, 0.92) 100%);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Configuration & Backend Constants
# -------------------------------------------------------------
API_BASE_URL = "http://localhost:8000"
USER_AVATAR_FILE = "user_avatar.png"

POPULAR_MODELS = [
    "default_env", # Special value to use backend .env configured OPENROUTER_MODEL_NAME
    "openai/gpt-4o-mini",
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-2.5-2.6b:free",
    "deepseek/deepseek-chat",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o",
    "meta-llama/llama-3.3-70b-instruct"
]

MODEL_DISPLAY_NAMES = {
    "default_env": "⚡ .env Configured Model (Backend Default)",
    "openai/gpt-4o-mini": "OpenAI: GPT-4o Mini (Fast & Smart)",
    "nvidia/nemotron-3.5-lightning:free": "Nvidia: Nemotron 3.5 Lightning (Free)",
    "liquid/lfm-2.5-2.6b:free": "Liquid: LFM 2.5 2.6B (Free)",
    "deepseek/deepseek-chat": "DeepSeek: V3 Chat (High Performance)",
    "anthropic/claude-3.5-sonnet": "Anthropic: Claude 3.5 Sonnet",
    "openai/gpt-4o": "OpenAI: GPT-4o Omni",
    "meta-llama/llama-3.3-70b-instruct": "Meta: Llama 3.3 70B Instruct"
}

# -------------------------------------------------------------
# 3. Session State Initialization
# -------------------------------------------------------------
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_name" not in st.session_state:
    st.session_state.user_name = "User"

if "is_email_verified" not in st.session_state:
    st.session_state.is_email_verified = False

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Conversation"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chats" not in st.session_state:
    st.session_state.chats = None

if "selected_model_key" not in st.session_state:
    st.session_state.selected_model_key = "default_env"

if "active_backend_model" not in st.session_state:
    st.session_state.active_backend_model = "Detecting..."

if "active_model_env_configured" not in st.session_state:
    st.session_state.active_model_env_configured = False

# -------------------------------------------------------------
# 4. Backend Communication Helpers (Full Backend Requirements)
# -------------------------------------------------------------
def get_auth_headers() -> dict:
    """Build HTTP headers with JWT Bearer token if user is authenticated."""
    headers = {"Content-Type": "application/json"}
    if st.session_state.get("auth_token"):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    return headers

def check_backend_health() -> Tuple[bool, str]:
    """Check backend health and fetch configured model from GET /."""
    try:
        resp = requests.get(f"{API_BASE_URL}/", timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            model = data.get("openrouter_model", "openai/gpt-4o-mini")
            st.session_state.active_backend_model = model
            return True, model
    except Exception:
        pass
    return False, "Unavailable"

def fetch_active_backend_model():
    """Fetch active OpenRouter model from GET /chats/model/active."""
    try:
        resp = requests.get(f"{API_BASE_URL}/chats/model/active", timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.active_backend_model = data.get("active_model", "openai/gpt-4o-mini")
            st.session_state.active_model_env_configured = data.get("is_env_configured", False)
    except Exception:
        pass

# --- 4.1 Authentication APIs ---
def login_user(email: str, password: str) -> Tuple[bool, str]:
    """Authenticate user with email & password via POST /user/login."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/login",
            json={"email": email.strip().lower(), "password": password},
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.is_logged_in = True
            st.session_state.auth_token = data.get("access_token")
            user_data = data.get("user", {})
            st.session_state.user_id = user_data.get("id")
            st.session_state.user_email = user_data.get("email", "")
            st.session_state.user_name = user_data.get("name", "User")
            st.session_state.is_email_verified = user_data.get("is_email_verified", False)
            
            # Reset active chat
            st.session_state.current_chat_id = None
            st.session_state.messages = []
            st.session_state.chats = None
            
            # Sync fresh profile from backend
            fetch_backend_profile()
            return True, "Login successful!"
        else:
            try:
                detail = resp.json().get("detail", "Invalid email or password")
            except Exception:
                detail = resp.text
            return False, detail
    except requests.RequestException as e:
        return False, f"Server communication error: {str(e)}"

def register_user(name: str, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """Register new user account via POST /user/register."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/register",
            json={"name": name.strip(), "email": email.strip().lower(), "password": password},
            timeout=8.0
        )
        if resp.status_code == 201:
            data = resp.json()
            return True, "Account registered successfully! Please verify your email with OTP.", None
        else:
            try:
                detail = resp.json().get("detail", "Registration failed")
            except Exception:
                detail = resp.text
            return False, detail, None
    except requests.RequestException as e:
        return False, f"Server communication error: {str(e)}", None

def verify_email_otp(email: str, otp: str) -> Tuple[bool, str]:
    """Verify email address with OTP via POST /user/verify-email."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/verify-email",
            json={"email": email.strip().lower(), "otp": otp.strip()},
            timeout=8.0
        )
        if resp.status_code == 200:
            st.session_state.is_email_verified = True
            return True, "Email verified successfully! You are all set."
        else:
            try:
                detail = resp.json().get("detail", "Verification failed")
            except Exception:
                detail = resp.text
            return False, detail
    except requests.RequestException as e:
        return False, f"Server communication error: {str(e)}"

def request_verification_otp(email: str) -> Tuple[bool, str, Optional[str]]:
    """Regenerate verification OTP via POST /user/verify-email/request."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/verify-email/request",
            json={"email": email.strip().lower()},
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            otp = data.get("otp")
            return True, "New verification OTP generated! (Valid 10 mins)", otp
        else:
            try:
                detail = resp.json().get("detail", "Request failed")
            except Exception:
                detail = resp.text
            return False, detail, None
    except requests.RequestException as e:
        return False, f"Server communication error: {str(e)}", None

def request_forgot_password(email: str) -> Tuple[bool, str, Optional[str]]:
    """Request password reset OTP via POST /user/forgot-password."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/forgot-password",
            json={"email": email.strip().lower()},
            timeout=8.0
        )
        if resp.status_code == 200:
            data = resp.json()
            otp = data.get("otp")
            return True, "Password reset OTP generated successfully! (Valid 10 mins)", otp
        else:
            try:
                detail = resp.json().get("detail", "Request failed")
            except Exception:
                detail = resp.text
            return False, detail, None
    except requests.RequestException as e:
        return False, f"Server communication error: {str(e)}", None

def reset_password(email: str, otp: str, new_password: str) -> Tuple[bool, str]:
    """Reset password using OTP via POST /user/reset-password."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/user/reset-password",
            json={"email": email.strip().lower(), "otp": otp.strip(), "new_password": new_password},
            timeout=8.0
        )
        if resp.status_code == 200:
            return True, "Password has been reset successfully! Please sign in with your new password."
        else:
            try:
                detail = resp.json().get("detail", "Password reset failed")
            except Exception:
                detail = resp.text
            return False, detail
    except requests.RequestException as e:
        return False, f"Server communication error: {str(e)}"

def logout_user():
    """Logout authenticated user via POST /user/logout and clear session."""
    try:
        if st.session_state.get("auth_token"):
            requests.post(
                f"{API_BASE_URL}/user/logout",
                headers=get_auth_headers(),
                timeout=3.0
            )
    except Exception:
        pass
    st.session_state.is_logged_in = False
    st.session_state.auth_token = None
    st.session_state.user_id = None
    st.session_state.user_email = ""
    st.session_state.user_name = "User"
    st.session_state.is_email_verified = False
    st.session_state.current_chat_id = None
    st.session_state.chats = None
    st.session_state.messages = []
    st.rerun()

# --- 4.2 User Profile APIs (GET & PUT /user/profile) ---
def fetch_backend_profile() -> Optional[dict]:
    """Retrieve full profile from MongoDB via GET /user/profile."""
    if not st.session_state.get("auth_token"):
        return None
    try:
        resp = requests.get(
            f"{API_BASE_URL}/user/profile",
            headers=get_auth_headers(),
            timeout=4.0
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.user_name = data.get("name", st.session_state.user_name)
            st.session_state.user_email = data.get("email", st.session_state.user_email)
            st.session_state.is_email_verified = data.get("is_email_verified", False)
            return data
        elif resp.status_code == 401:
            st.session_state.is_logged_in = False
            st.rerun()
    except Exception:
        pass
    return None

def update_backend_profile(name: str) -> Tuple[bool, str]:
    """Update profile name in MongoDB via PUT /user/profile."""
    if not st.session_state.get("auth_token"):
        return False, "Not authenticated"
    try:
        resp = requests.put(
            f"{API_BASE_URL}/user/profile",
            json={"name": name.strip()},
            headers=get_auth_headers(),
            timeout=5.0
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.user_name = data.get("name", name.strip())
            return True, "Profile updated successfully in MongoDB!"
        else:
            try:
                detail = resp.json().get("detail", "Update failed")
            except Exception:
                detail = resp.text
            return False, detail
    except requests.RequestException as e:
        return False, f"Network error: {str(e)}"

# --- 4.3 Chat Management APIs (Authenticated) ---
def fetch_user_chats(user_id: str, force_reload: bool = False) -> List[Dict]:
    """Fetch user chats via GET /chats/{user_id}."""
    if not force_reload and st.session_state.chats is not None:
        return st.session_state.chats

    try:
        resp = requests.get(
            f"{API_BASE_URL}/chats/{user_id.strip()}",
            headers=get_auth_headers(),
            timeout=5.0
        )
        if resp.status_code == 200:
            chats = resp.json()
            st.session_state.chats = chats
            return chats
        elif resp.status_code == 401:
            st.session_state.is_logged_in = False
            st.rerun()
        return []
    except requests.RequestException:
        return st.session_state.chats or []

def create_new_chat(user_id: str) -> Optional[Dict]:
    """Create a new chat session via POST /chats/new."""
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
        elif resp.status_code == 401:
            st.session_state.is_logged_in = False
            st.rerun()
        return None
    except requests.RequestException as e:
        st.error(f"Error creating chat: {str(e)}")
        return None

def fetch_chat_messages(chat_id: str) -> List[Dict]:
    """Fetch message history for active chat via GET /chats/{chat_id}/messages."""
    try:
        resp = requests.get(
            f"{API_BASE_URL}/chats/{chat_id.strip()}/messages",
            headers=get_auth_headers(),
            timeout=5.0
        )
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            st.session_state.is_logged_in = False
            st.rerun()
        return []
    except requests.RequestException as e:
        st.error(f"Error loading messages: {str(e)}")
        return []

def send_chat_message(
    chat_id: Optional[str],
    user_id: str,
    message: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Send user message via POST /chats/send and receive AI reply, resolved chat_id, and model used.
    If model_name is None, backend uses OPENROUTER_MODEL_NAME from .env.
    """
    try:
        payload = {
            "chat_id": chat_id or "",
            "user_id": user_id,
            "message": message
        }
        if model_name and model_name.strip():
            payload["model_name"] = model_name.strip()
        if api_key and api_key.strip():
            payload["api_key"] = api_key.strip()

        resp = requests.post(
            f"{API_BASE_URL}/chats/send",
            json=payload,
            headers=get_auth_headers(),
            timeout=60.0
        )
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("reply", "")
            returned_cid = data.get("chat_id")
            model_used = data.get("model")
            return reply, returned_cid, model_used
        elif resp.status_code == 401:
            st.session_state.is_logged_in = False
            st.rerun()
            return None, None, None
        else:
            try:
                err_detail = resp.json().get("detail", resp.text)
            except Exception:
                err_detail = resp.text
            st.error(f"AI Service Error: {err_detail}")
            return None, None, None
    except requests.RequestException as e:
        st.error(f"Failed to communicate with backend: {str(e)}")
        return None, None, None

def delete_chat(chat_id: str) -> bool:
    """Delete a chat session and all messages via DELETE /chats/{chat_id}."""
    try:
        resp = requests.delete(
            f"{API_BASE_URL}/chats/{chat_id.strip()}",
            headers=get_auth_headers(),
            timeout=5.0
        )
        if resp.status_code == 200:
            st.session_state.chats = None
            return True
        elif resp.status_code == 401:
            st.session_state.is_logged_in = False
            st.rerun()
        return False
    except requests.RequestException:
        return False

def format_chat_timestamp(iso_str: Optional[str]) -> str:
    """Format ISO timestamp into clean readable text."""
    if not iso_str:
        return "Recent"
    try:
        clean_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        return dt.strftime("%d %b • %I:%M %p")
    except Exception:
        return iso_str[:10]

# -------------------------------------------------------------
# 5. Check Health & Avatars
# -------------------------------------------------------------
backend_online, active_env_model = check_backend_health()
if backend_online:
    fetch_active_backend_model()

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
# 6. Sidebar Layout
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 1.8rem;">⚡</span>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; color: #00f2fe; letter-spacing: 1px;">NEXUS CORE</div>
                <div style="font-size: 0.72rem; color: #64748b; font-family: monospace;">FULL-STACK AI ENGINE v2.0</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Server Status Badge
    if backend_online:
        st.markdown(
            f'<div class="tech-badge-green" style="margin-bottom: 8px;">● SYSTEM ONLINE (PORT 8000)</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="tech-badge-cyan" style="color: #f87171; border-color: #f87171; margin-bottom: 8px;">● BACKEND OFFLINE (PORT 8000)</div>',
            unsafe_allow_html=True
        )

    # Active Backend Model Status Box
    env_model_display = st.session_state.active_backend_model
    st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1e293b; border-left: 3px solid #00f2fe; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px;">
            <div style="font-size: 0.68rem; color: #64748b; font-family: monospace; text-transform: uppercase;">BACKEND .ENV MODEL</div>
            <div style="font-size: 0.82rem; font-weight: 700; color: #38bdf8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{env_model_display}">
                {env_model_display}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.is_logged_in:
        # LOCKED SIDEBAR WHEN LOGGED OUT
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid #1e293b; border-left: 3px solid #f59e0b; padding: 14px 16px; border-radius: 8px; margin-top: 10px;">
                <div style="color: #fbbf24; font-weight: 700; font-size: 0.88rem; margin-bottom: 4px;">🔒 AUTHENTICATION REQUIRED</div>
                <div style="color: #94a3b8; font-size: 0.78rem; line-height: 1.5;">
                    Conversation sessions, neural memory buffer, and saved history are restricted to registered users.
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # AUTHENTICATED USER SIDEBAR
        user_display_name = st.session_state.user_name or "User"
        verified_badge = '<span class="tech-badge-green" style="font-size: 0.65rem; padding: 1px 5px;">✓ VERIFIED</span>' if st.session_state.is_email_verified else '<span class="tech-badge-amber" style="font-size: 0.65rem; padding: 1px 5px;">! UNVERIFIED</span>'

        if avatar_base64_src:
            avatar_markup = f'<img src="{avatar_base64_src}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 2px solid #00f2fe; box-shadow: 0 0 10px rgba(0,242,254,0.3);">'
        else:
            avatar_markup = '<div style="width: 42px; height: 42px; border-radius: 50%; background: #131d2e; border: 1.5px solid #00f2fe; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">👨‍💻</div>'

        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 12px;">
                {avatar_markup}
                <div style="overflow: hidden;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-weight: 700; font-size: 0.92rem; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_display_name}</span>
                        {verified_badge}
                    </div>
                    <div style="font-size: 0.72rem; color: #00f2fe; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.user_email}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Model Selector for User Query
        st.markdown("<span style='font-size: 0.8rem; font-weight: 600; color: #94a3b8; font-family: monospace;'>⚡ NEURAL MODEL ROUTE</span>", unsafe_allow_html=True)
        
        current_model_idx = 0
        if st.session_state.selected_model_key in POPULAR_MODELS:
            current_model_idx = POPULAR_MODELS.index(st.session_state.selected_model_key)
        
        selected_key = st.selectbox(
            "Select Model:",
            options=POPULAR_MODELS,
            format_func=lambda k: MODEL_DISPLAY_NAMES.get(k, k),
            index=current_model_idx,
            label_visibility="collapsed"
        )
        st.session_state.selected_model_key = selected_key

        st.divider()

        # Chat History List
        col_hist_title, col_refresh = st.columns([0.78, 0.22])
        with col_hist_title:
            st.markdown("<span style='font-size: 0.82rem; font-weight: 700; color: #38bdf8; letter-spacing: 0.8px;'>📁 CHAT HISTORY</span>", unsafe_allow_html=True)
        with col_refresh:
            if st.button("🔄", key="refresh_chats_btn", help="Reload Chat History"):
                st.session_state.chats = None
                st.rerun()

        if backend_online and st.session_state.user_id:
            chat_sessions = fetch_user_chats(st.session_state.user_id)
            if not chat_sessions:
                st.markdown("""
                    <div style="padding: 16px 10px; text-align: center; color: #64748b; font-size: 0.82rem;">
                        <em>No archived sessions found.</em><br>
                        Click <strong>+ New Chat</strong> to begin.
                    </div>
                """, unsafe_allow_html=True)
            else:
                for chat in chat_sessions:
                    cid = chat["chat_id"]
                    ctitle = chat.get("title", "New Conversation")
                    created_at_raw = chat.get("created_at")
                    formatted_time = format_chat_timestamp(created_at_raw)
                    is_active = (cid == st.session_state.current_chat_id)
                    short_id = cid[-6:] if len(cid) >= 6 else cid

                    active_class = "history-card-active" if is_active else ""
                    st.markdown(f"""
                        <div class="history-card {active_class}">
                            <div class="history-title">{"⚡ " if is_active else "💬 "}{ctitle}</div>
                            <div class="history-meta">
                                <span>🕒 {formatted_time}</span>
                                <span>#{short_id}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    col_open, col_del = st.columns([0.80, 0.20])
                    with col_open:
                        btn_text = "✓ Active" if is_active else "Open Chat"
                        if st.button(btn_text, key=f"open_chat_{cid}", use_container_width=True, disabled=is_active):
                            st.session_state.current_chat_id = cid
                            st.session_state.current_chat_title = ctitle
                            st.session_state.messages = fetch_chat_messages(cid)
                            st.rerun()
                    with col_del:
                        if st.button("✕", key=f"del_chat_{cid}", help=f"Delete '{ctitle}'"):
                            if delete_chat(cid):
                                if st.session_state.current_chat_id == cid:
                                    st.session_state.current_chat_id = None
                                    st.session_state.messages = []
                                st.rerun()
                    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e293b; border-left: 3px solid #00f2fe; padding: 10px 12px; border-radius: 6px; font-size: 0.78rem; color: #94a3b8; font-family: monospace;">
                🧠 <strong>NEURAL MEMORY BUFFER</strong><br>
                Preserves last 10 dialog turns for context.
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            logout_user()


# =============================================================
# 7. ROUTING: LOGGED OUT -> AUTHENTICATION PORTAL
# =============================================================
if not st.session_state.is_logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 25px 20px 15px 20px;">
            <div style="display: inline-block; width: 70px; height: 70px; line-height: 70px; border-radius: 50%; background: radial-gradient(circle, rgba(0,242,254,0.2) 0%, rgba(0,0,0,0) 70%); border: 1px solid #00f2fe; font-size: 2.2rem; box-shadow: 0 0 25px rgba(0, 242, 254, 0.35); margin-bottom: 12px;">
                ⚡
            </div>
            <h1 style="color: #ffffff; font-weight: 800; font-size: 2.3rem; margin: 0; letter-spacing: -0.5px;">
                NEXUS AI <span style="color: #00f2fe;">AUTHENTICATION</span>
            </h1>
            <p style="color: #94a3b8; font-size: 1.0rem; max-width: 600px; margin: 10px auto 18px auto;">
                Sign in or create an account to access AI Chat, MongoDB persistent conversation history, and neural context memory.
            </p>
            <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
                <span class="tech-badge-cyan">SECURITY: JWT BEARER</span>
                <span class="tech-badge-green">BACKEND: FASTAPI + MONGODB</span>
                <span class="tech-badge-amber">STATUS: AUTH REQUIRED</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_pad_l, col_auth, col_pad_r = st.columns([0.22, 0.56, 0.22])

    with col_auth:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        tab_login, tab_register, tab_verify, tab_forgot = st.tabs([
            "🔐 Sign In",
            "✨ Create Account",
            "✉️ Verify Email",
            "🔑 Forgot Password"
        ])

        # -----------------------------------------------------
        # TAB 1: LOGIN
        # -----------------------------------------------------
        with tab_login:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address:", key="auth_login_email", placeholder="user@example.com")
            login_password = st.text_input("Password:", type="password", key="auth_login_pass", placeholder="••••••••")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Sign In to NEXUS AI", key="btn_do_login", type="primary", use_container_width=True, disabled=not backend_online):
                if not login_email.strip() or not login_password.strip():
                    st.warning("Please provide both email and password.")
                else:
                    with st.spinner("Authenticating credentials..."):
                        success, message = login_user(login_email, login_password)
                    if success:
                        st.success("Authentication successful! Loading chat workspace...")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"Login Failed: {message}")

        # -----------------------------------------------------
        # TAB 2: REGISTER
        # -----------------------------------------------------
        with tab_register:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Name:", key="auth_reg_name", placeholder="Mohit Yadav")
            reg_email = st.text_input("Email Address:", key="auth_reg_email", placeholder="user@example.com")
            reg_password = st.text_input("Password:", type="password", key="auth_reg_pass", placeholder="Minimum 6 characters")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("✨ Create Account", key="btn_do_register", type="primary", use_container_width=True, disabled=not backend_online):
                if not reg_name.strip() or not reg_email.strip() or not reg_password.strip():
                    st.warning("All fields are required to register.")
                else:
                    with st.spinner("Registering user in MongoDB..."):
                        success, message, dev_otp = register_user(reg_name, reg_email, reg_password)
                    if success:
                        st.success(message)
                        if dev_otp:
                            st.info(f"🔑 Your Email Verification OTP is: **`{dev_otp}`**")
                        st.info("You can now verify your email in the 'Verify Email' tab or sign in directly.")
                    else:
                        st.error(f"Registration Error: {message}")

        # -----------------------------------------------------
        # TAB 3: VERIFY EMAIL OTP
        # -----------------------------------------------------
        with tab_verify:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            ver_email = st.text_input("Registered Email to Verify:", key="auth_ver_email", placeholder="user@example.com")
            ver_otp = st.text_input("6-Digit OTP:", key="auth_ver_otp", placeholder="123456", max_chars=6)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            col_v1, col_v2 = st.columns([0.65, 0.35])
            with col_v1:
                if st.button("✓ Confirm OTP", key="btn_do_verify", type="primary", use_container_width=True, disabled=not backend_online):
                    if not ver_email.strip() or not ver_otp.strip():
                        st.warning("Please enter your email and 6-digit OTP.")
                    else:
                        with st.spinner("Verifying OTP..."):
                            success, message = verify_email_otp(ver_email, ver_otp)
                        if success:
                            st.success(message)
                        else:
                            st.error(f"Verification Failed: {message}")
            with col_v2:
                if st.button("Resend OTP", key="btn_resend_otp", use_container_width=True, disabled=not backend_online):
                    if not ver_email.strip():
                        st.warning("Please provide email.")
                    else:
                        with st.spinner("Requesting new OTP..."):
                            success, message, new_otp = request_verification_otp(ver_email)
                        if success:
                            st.success(message)
                            if new_otp:
                                st.info(f"🔑 OTP: **`{new_otp}`**")
                        else:
                            st.error(message)

        # -----------------------------------------------------
        # TAB 4: FORGOT PASSWORD
        # -----------------------------------------------------
        with tab_forgot:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            fp_email = st.text_input("Account Email:", key="auth_fp_email", placeholder="user@example.com")
            
            if st.button("📨 Send Reset OTP", key="btn_fp_req", use_container_width=True, disabled=not backend_online):
                if not fp_email.strip():
                    st.warning("Please enter your email.")
                else:
                    with st.spinner("Generating password reset OTP..."):
                        success, message, fp_otp = request_forgot_password(fp_email)
                    if success:
                        st.success(message)
                        if fp_otp:
                            st.info(f"🔑 Password Reset OTP: **`{fp_otp}`**")
                    else:
                        st.error(message)

            st.markdown("<hr style='margin: 12px 0; border-color: #1e293b;'>", unsafe_allow_html=True)
            fp_otp_input = st.text_input("Enter 6-Digit OTP:", key="auth_fp_otp_input", placeholder="123456", max_chars=6)
            fp_new_pass = st.text_input("New Password:", type="password", key="auth_fp_new_pass", placeholder="Enter new strong password")

            if st.button("🔒 Reset Password", key="btn_fp_submit", type="primary", use_container_width=True, disabled=not backend_online):
                if not fp_email.strip() or not fp_otp_input.strip() or not fp_new_pass.strip():
                    st.warning("All fields are required to reset password.")
                else:
                    with st.spinner("Updating password..."):
                        success, message = reset_password(fp_email, fp_otp_input, fp_new_pass)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================
# 8. ROUTING: LOGGED IN -> FULL APPLICATION WORKSPACE
# =============================================================
else:
    # ---------------------------------------------------------
    # Unverified Email Warning Banner (If applicable)
    # ---------------------------------------------------------
    if not st.session_state.is_email_verified:
        col_warn1, col_warn2 = st.columns([0.82, 0.18])
        with col_warn1:
            st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 10px 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">⚠️</span>
                    <span style="color: #fbbf24; font-size: 0.88rem;">
                        <strong>Email Unverified:</strong> Your email <code>{st.session_state.user_email}</code> is pending verification.
                    </span>
                </div>
            """, unsafe_allow_html=True)
        with col_warn2:
            with st.popover("✉️ Verify Now", use_container_width=True):
                st.markdown("##### ✉️ Quick Email Verification")
                q_otp = st.text_input("Enter 6-Digit OTP:", key="quick_verify_otp", max_chars=6)
                col_qv1, col_qv2 = st.columns(2)
                with col_qv1:
                    if st.button("Verify", key="btn_quick_verify", type="primary", use_container_width=True):
                        s, m = verify_email_otp(st.session_state.user_email, q_otp)
                        if s:
                            st.toast("Email verified! ✅")
                            st.rerun()
                        else:
                            st.error(m)
                with col_qv2:
                    if st.button("Resend", key="btn_quick_resend", use_container_width=True):
                        s, m, o = request_verification_otp(st.session_state.user_email)
                        if s:
                            st.toast("OTP sent! 📨")
                            if o:
                                st.info(f"OTP: `{o}`")
                        else:
                            st.error(m)

    # ---------------------------------------------------------
    # Top Bar: Brand, Center NEW CHAT, Top-Right Popover & Quick Logout
    # ---------------------------------------------------------
    top_col1, top_col2, top_col3 = st.columns([0.22, 0.46, 0.32])

    with top_col1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; height: 42px;">
                <span style="color: #00f2fe; font-size: 1.3rem;">⚡</span>
                <span style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.5px; color: #f8fafc;">NEXUS // AI</span>
            </div>
        """, unsafe_allow_html=True)

    with top_col2:
        if st.button("⚡ + NEW CHAT", key="center_new_chat_btn", type="primary", use_container_width=True, disabled=not backend_online):
            new_chat_res = create_new_chat(st.session_state.user_id)
            if new_chat_res:
                st.session_state.current_chat_id = new_chat_res["chat_id"]
                st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")
                st.session_state.messages = []
                st.session_state.chats = None
                st.rerun()

    with top_col3:
        col_user_pill, col_menu_btn, col_logout_quick = st.columns([0.48, 0.28, 0.24])
        
        with col_user_pill:
            if avatar_base64_src:
                small_pic = f'<img src="{avatar_base64_src}" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1.5px solid #00f2fe; vertical-align: middle; margin-right: 6px;">'
            else:
                small_pic = '<span style="font-size: 1.1rem; vertical-align: middle; margin-right: 6px;">👨‍💻</span>'

            st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: flex-end; height: 42px; overflow: hidden;">
                    {small_pic}
                    <span style="font-size: 0.85rem; font-weight: 700; color: #f1f5f9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95px;">
                        {st.session_state.user_name}
                    </span>
                </div>
            """, unsafe_allow_html=True)

        with col_menu_btn:
            with st.popover("⋮ Menu", help="Profile & System Settings", use_container_width=True):
                st.markdown("""
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 1.2rem;">⚙️</span>
                        <span style="font-weight: 800; font-size: 1.05rem; color: #00f2fe;">SETTINGS & PROFILE</span>
                    </div>
                """, unsafe_allow_html=True)

                tab_profile, tab_system = st.tabs(["👤 Profile (MongoDB)", "⚡ System & Model"])

                with tab_profile:
                    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                    if avatar_base64_src:
                        big_pic = f'<img src="{avatar_base64_src}" style="width: 75px; height: 75px; border-radius: 50%; object-fit: cover; border: 2.5px solid #00f2fe; box-shadow: 0 0 16px rgba(0,242,254,0.4); display: block; margin: 0 auto;">'
                    else:
                        big_pic = '<div style="width: 75px; height: 75px; border-radius: 50%; background: #131d2e; border: 2px dashed #00f2fe; display: flex; align-items: center; justify-content: center; font-size: 2.2rem; margin: 0 auto;">👤</div>'

                    st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 10px;">
                            {big_pic}
                            <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 6px;">Profile Photo Preview</div>
                        </div>
                    """, unsafe_allow_html=True)

                    uploaded_photo = st.file_uploader(
                        "Update Avatar Image:",
                        type=["png", "jpg", "jpeg", "webp"],
                        key="popover_photo_uploader"
                    )

                    edit_name = st.text_input(
                        "Full Name (Synced to MongoDB):",
                        value=st.session_state.user_name,
                        key="input_profile_name"
                    )

                    st.markdown(f"""
                        <div style="font-size: 0.78rem; color: #64748b; font-family: monospace; line-height: 1.6; margin-bottom: 10px;">
                            • Email: <span style="color: #cbd5e1;">{st.session_state.user_email}</span><br>
                            • Verified: <span style="color: {'#10b981' if st.session_state.is_email_verified else '#fbbf24'};">{'YES' if st.session_state.is_email_verified else 'NO'}</span><br>
                            • User ID: <span style="color: #00f2fe;">{st.session_state.user_id}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    col_save, col_clear = st.columns([0.65, 0.35])
                    with col_save:
                        if st.button("💾 Save Profile", key="btn_save_user_profile", type="primary", use_container_width=True):
                            if uploaded_photo is not None:
                                photo_data = uploaded_photo.read()
                                with open(USER_AVATAR_FILE, "wb") as pf:
                                    pf.write(photo_data)

                            if edit_name.strip() and edit_name.strip() != st.session_state.user_name:
                                s, msg = update_backend_profile(edit_name.strip())
                                if s:
                                    st.toast("Profile updated in MongoDB! ✅", icon="💾")
                                else:
                                    st.error(msg)
                            else:
                                st.toast("Saved! ✅", icon="💾")
                            st.rerun()

                    with col_clear:
                        if has_custom_avatar:
                            if st.button("Remove Pic", key="btn_remove_photo", use_container_width=True):
                                if os.path.exists(USER_AVATAR_FILE):
                                    os.remove(USER_AVATAR_FILE)
                                st.toast("Avatar removed", icon="🗑️")
                                st.rerun()

                with tab_system:
                    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style="font-size: 0.78rem; color: #64748b; font-family: monospace; line-height: 1.8;">
                            • Active Backend Model (.env): <span style="color: #00f2fe;">{st.session_state.active_backend_model}</span><br>
                            • Current Route Selection: <span style="color: #10b981;">{MODEL_DISPLAY_NAMES.get(st.session_state.selected_model_key, st.session_state.selected_model_key)}</span><br>
                            • Backend Server: <span style="color: {'#10b981' if backend_online else '#f87171'};">{'CONNECTED' if backend_online else 'DISCONNECTED'}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    custom_api_key = st.text_input(
                        "OpenRouter API Key (Optional Override):",
                        value=st.session_state.get("custom_api_key", ""),
                        type="password",
                        key="input_custom_api_key",
                        help="Backend .env key is used by default. Enter here only to override."
                    )
                    st.session_state["custom_api_key"] = custom_api_key

        with col_logout_quick:
            if st.button("🚪", key="btn_quick_logout", help="Log out"):
                logout_user()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Main Screen: Hero Welcome vs Active Conversation
    # ---------------------------------------------------------
    active_model_resolved = st.session_state.active_backend_model if st.session_state.selected_model_key == "default_env" else st.session_state.selected_model_key

    if not st.session_state.current_chat_id:
        st.markdown(f"""
            <div style="text-align: center; padding: 25px 20px 10px 20px;">
                <div style="display: inline-block; width: 70px; height: 70px; line-height: 70px; border-radius: 50%; background: radial-gradient(circle, rgba(0,242,254,0.2) 0%, rgba(0,0,0,0) 70%); border: 1px solid #00f2fe; font-size: 2.2rem; box-shadow: 0 0 25px rgba(0, 242, 254, 0.35); margin-bottom: 12px;">
                    ⚡
                </div>
                <h1 style="color: #ffffff; font-weight: 800; font-size: 2.3rem; margin: 0; letter-spacing: -0.5px;">
                    NEXUS AI <span style="color: #00f2fe;">WORKSPACE</span>
                </h1>
                <p style="color: #94a3b8; font-size: 1.05rem; max-width: 600px; margin: 10px auto 18px auto;">
                    Welcome back, <strong style="color: #f8fafc;">{st.session_state.user_name}</strong>! Type in the chat input below or click Initiate to start a fresh dialog.
                </p>
                <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
                    <span class="tech-badge-cyan">MODEL: {active_model_resolved}</span>
                    <span class="tech-badge-green">AUTHENTICATED: YES</span>
                    <span class="tech-badge-cyan">USER: #{str(st.session_state.user_id)[-6:] if st.session_state.user_id else ''}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        center_c1, center_c2, center_c3 = st.columns([0.22, 0.56, 0.22])
        with center_c2:
            if st.button("🚀 INITIATE NEW CONVERSATION", key="hero_start_btn", type="primary", use_container_width=True, disabled=not backend_online):
                new_chat_res = create_new_chat(st.session_state.user_id)
                if new_chat_res:
                    st.session_state.current_chat_id = new_chat_res["chat_id"]
                    st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")
                    st.session_state.messages = []
                    st.session_state.chats = None
                    st.rerun()

    else:
        # ACTIVE CONVERSATION VIEW
        short_session_id = st.session_state.current_chat_id[-8:]

        st.markdown(f"""
            <div class="tech-header-card">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div class="tech-title">
                            <span>⚡</span> {st.session_state.current_chat_title}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; font-family: monospace; margin-top: 5px;">
                            SESSION: <span style="color: #00f2fe;">#{short_session_id}</span> &nbsp;|&nbsp; ROUTE: <span style="color: #cbd5e1;">{active_model_resolved}</span>
                        </div>
                    </div>
                    <div>
                        <span class="tech-badge-green">● LIVE CONTEXT BUFFER</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Message List
        for msg in st.session_state.messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            msg_model = msg.get("model")
            avatar_icon = user_avatar_target if role == "user" else "⚡"
            
            with st.chat_message(role, avatar=avatar_icon):
                st.markdown(content)
                if role == "assistant" and msg_model:
                    st.markdown(f'<div class="model-tag">⚡ Generated via: {msg_model}</div>', unsafe_allow_html=True)

    # Active Chat Input (Available for all authenticated views)
    user_input = st.chat_input("Ask NEXUS anything (Tech query, coding, logic, reasoning)...", disabled=not backend_online)

    if user_input:
        clean_input = user_input.strip()
        if clean_input:
            st.session_state.messages.append({
                "role": "user",
                "content": clean_input
            })
            with st.chat_message("user", avatar=user_avatar_target):
                st.markdown(clean_input)

            with st.chat_message("assistant", avatar="⚡"):
                with st.spinner("⚡ Neural Core generating response..."):
                    # Resolve model parameter
                    model_param = None if st.session_state.selected_model_key == "default_env" else st.session_state.selected_model_key
                    
                    ai_reply, returned_chat_id, model_used = send_chat_message(
                        chat_id=st.session_state.current_chat_id,
                        user_id=st.session_state.user_id,
                        message=clean_input,
                        model_name=model_param,
                        api_key=st.session_state.get("custom_api_key")
                    )

                if ai_reply:
                    st.markdown(ai_reply)
                    if model_used:
                        st.markdown(f'<div class="model-tag">⚡ Generated via: {model_used}</div>', unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_reply,
                        "model": model_used
                    })

                    if returned_chat_id:
                        st.session_state.current_chat_id = returned_chat_id

                    st.session_state.chats = None
                    refreshed = fetch_user_chats(st.session_state.user_id, force_reload=True)
                    for c in refreshed:
                        if c["chat_id"] == st.session_state.current_chat_id:
                            st.session_state.current_chat_title = c.get("title", st.session_state.current_chat_title)
                            break
                    st.rerun()
