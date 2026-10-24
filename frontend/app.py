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
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    
    .tech-title {
        font-size: 1.4rem;
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
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-family: monospace;
        font-weight: 600;
    }

    .tech-badge-red {
        display: inline-block;
        background: rgba(239, 68, 68, 0.12);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-family: monospace;
        font-weight: 600;
    }

    /* 4. Old Chats Text Format Container */
    .history-card {
        background-color: #0e1422;
        border: 1px solid #1a2538;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
        transition: all 0.15s ease-in-out;
    }
    
    .history-card:hover {
        border-color: #00f2fe;
        background-color: #121b2d;
    }

    .history-card-active {
        background-color: #132238 !important;
        border: 1px solid #00f2fe !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.15);
    }

    .history-title {
        color: #e2e8f0;
        font-size: 0.88rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }

    .history-meta {
        font-size: 0.74rem;
        color: #64748b;
        font-family: monospace;
        margin-top: 3px;
        display: flex;
        justify-content: space-between;
    }

    /* 5. Chat Messages Tech Glow */
    [data-testid="stChatMessage"] {
        background-color: #0c121e !important;
        border: 1px solid #182234 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 3px solid #00f2fe !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 3px solid #10b981 !important;
    }

    /* Modern Buttons */
    .stButton > button {
        background-color: #0e1726 !important;
        color: #38bdf8 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #132238 !important;
        border-color: #00f2fe !important;
        color: #ffffff !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(0, 114, 255, 0.4) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #0099ff 100%) !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5) !important;
    }

    /* 3-Dots Settings Popover Button */
    div[data-testid="stPopover"] > button {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        color: #94a3b8 !important;
        font-size: 1.15rem !important;
        padding: 5px 12px !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stPopover"] > button:hover {
        border-color: #00f2fe !important;
        color: #ffffff !important;
        box-shadow: 0 0 18px rgba(0, 242, 254, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="stPopoverBody"] {
        background-color: #0b0f19 !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.7) !important;
        color: #e2e8f0 !important;
        padding: 16px !important;
    }

    /* Floating input container */
    .stChatFloatingInputContainer {
        bottom: 15px;
        background: transparent !important;
    }

    /* ChatGPT Auth Screen Styling */
    .chatgpt-auth-card {
        background: #17171a;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 32px 28px;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6);
        margin: 10px auto 25px auto;
    }
    .chatgpt-badge-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #10a37f;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px auto;
        font-size: 24px;
        box-shadow: 0 4px 18px rgba(16, 163, 127, 0.35);
    }
    .chatgpt-auth-title {
        color: #ffffff;
        font-size: 1.85rem;
        font-weight: 700;
        text-align: center;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .chatgpt-auth-desc {
        color: #8e8ea0;
        font-size: 0.90rem;
        text-align: center;
        margin-bottom: 22px;
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
    st.session_state.auth_mode = "login"

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
        resp = requests.get(f"{API_BASE_URL}/chats/{user_id.strip()}", timeout=4.0)
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
        resp = requests.get(f"{API_BASE_URL}/chats/{chat_id.strip()}/messages", timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
        return []
    except requests.RequestException as e:
        st.error(f"Error loading messages: {str(e)}")
        return []


def send_chat_message(chat_id: str, user_id: str, message: str, model_name: str) -> Optional[str]:
    """Send user message and receive AI reply."""
    try:
        payload = {
            "chat_id": chat_id,
            "user_id": user_id,
            "message": message,
            "model_name": model_name
        }
        resp = requests.post(f"{API_BASE_URL}/chats/send", json=payload, timeout=75.0)
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
        resp = requests.delete(f"{API_BASE_URL}/chats/{chat_id.strip()}", timeout=4.0)
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
# 7. AUTHENTICATION GATEWAY (WHEN USER IS NOT LOGGED IN)
# -------------------------------------------------------------
backend_online = check_backend_health()

if not st.session_state.is_authenticated:
    # ---------------------------------------------------------
    # ChatGPT-Style Centered Real-World Auth Screen
    # ---------------------------------------------------------
    # 3-Column Layout to center a compact card in the middle
    auth_col1, auth_col2, auth_col3 = st.columns([0.31, 0.38, 0.31])

    with auth_col2:
        # Subtle Backend Offline Notice if needed
        if not backend_online:
            st.warning(f"⚠️ **Backend Offline ({API_BASE_URL})**: Please start the FastAPI backend server (`run_backend.bat`).")

        auth_mode = st.session_state.get("auth_mode", "login")

        # -----------------------------------------------------
        # VIEW 1: CHATGPT LOGIN
        # -----------------------------------------------------
        if auth_mode == "login":
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; margin-bottom: 22px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 26px; color: #ffffff; margin-bottom: 12px;">
                        ⚡
                    </div>
                    <h1 style="color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Welcome back</h1>
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Log in to continue to NEXUS AI</div>
                </div>
            """, unsafe_allow_html=True)

            login_email = st.text_input("Email address", key="auth_login_email", placeholder="name@example.com")
            login_password = st.text_input("Password", type="password", key="auth_login_password", placeholder="Enter your password")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            if st.button("Continue", key="btn_chatgpt_login", type="primary", use_container_width=True, disabled=not backend_online):
                if not login_email.strip() or not login_password:
                    st.error("Please enter your email and password.")
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

            # Links below Continue Button
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            c_link1, c_link2 = st.columns([0.65, 0.35])
            with c_link1:
                st.markdown("<span style='color: #8e8ea0; font-size: 0.88rem;'>Don't have an account?</span>", unsafe_allow_html=True)
            with c_link2:
                if st.button("Sign up", key="btn_goto_register", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()

            st.markdown("<div style='text-align: center; margin-top: 10px;'>", unsafe_allow_html=True)
            if st.button("Forgot password?", key="btn_goto_forgot", use_container_width=True):
                st.session_state.auth_mode = "forgot"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top: 16px; border-top: 1px solid #232733; padding-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button("Continue as Guest", key="btn_guest_login", use_container_width=True):
                st.session_state.is_authenticated = True
                st.session_state.user_id = "guest_user"
                st.session_state.user_email = "guest@nexus.ai"
                st.session_state.user_full_name = "Guest Explorer"
                st.session_state.user_first_name = "Guest"
                st.session_state.user_surname = "Explorer"
                st.session_state.is_email_verified = True
                st.rerun()

        # -----------------------------------------------------
        # VIEW 2: CHATGPT CREATE ACCOUNT (REGISTER)
        # -----------------------------------------------------
        elif auth_mode == "register":
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; margin-bottom: 22px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 26px; color: #ffffff; margin-bottom: 12px;">
                        ⚡
                    </div>
                    <h1 style="color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Create your account</h1>
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Join NEXUS AI to get started</div>
                </div>
            """, unsafe_allow_html=True)

            reg_name = st.text_input("Full Name", key="auth_reg_name", placeholder="e.g. Shivkant Shrivas")
            reg_email = st.text_input("Email address", key="auth_reg_email", placeholder="name@example.com")
            reg_password = st.text_input("Password (min 6 chars)", type="password", key="auth_reg_password", placeholder="Create a password")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            if st.button("Continue", key="btn_chatgpt_register", type="primary", use_container_width=True, disabled=not backend_online):
                if not reg_name.strip() or not reg_email.strip() or len(reg_password) < 6:
                    st.error("Please fill all fields. Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        res = api_user_register(reg_name, reg_email, reg_password)
                    if res["success"]:
                        st.success("🎉 Account created! Please verify your email with the OTP sent.")
                        st.session_state.auth_mode = "verify"
                        st.session_state._last_registered_email = reg_email.strip()
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(f"❌ {res['error']}")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            c_r1, c_r2 = st.columns([0.65, 0.35])
            with c_r1:
                st.markdown("<span style='color: #8e8ea0; font-size: 0.88rem;'>Already have an account?</span>", unsafe_allow_html=True)
            with c_r2:
                if st.button("Log in", key="btn_reg_goto_login", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()

        # -----------------------------------------------------
        # VIEW 3: CHATGPT VERIFY OTP
        # -----------------------------------------------------
        elif auth_mode == "verify":
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; margin-bottom: 22px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 26px; color: #ffffff; margin-bottom: 12px;">
                        🛡️
                    </div>
                    <h1 style="color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Verify your email</h1>
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Enter the 6-digit OTP code sent to your email</div>
                </div>
            """, unsafe_allow_html=True)

            default_ver_email = st.session_state.get("_last_registered_email", "")
            ver_email = st.text_input("Email address", value=default_ver_email, key="auth_ver_email", placeholder="name@example.com")
            ver_otp = st.text_input("6-digit code", key="auth_ver_otp", placeholder="123456", max_chars=6)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            col_v1, col_v2 = st.columns([0.65, 0.35])
            with col_v1:
                if st.button("Verify code", key="btn_chatgpt_verify", type="primary", use_container_width=True, disabled=not backend_online):
                    if not ver_email.strip() or not ver_otp.strip():
                        st.error("Please enter email and 6-digit OTP.")
                    else:
                        with st.spinner("Verifying OTP..."):
                            res = api_verify_email(ver_email, ver_otp)
                        if res["success"]:
                            st.success("✅ Email verified! You can now log in.")
                            st.session_state.auth_mode = "login"
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"❌ {res['error']}")
            with col_v2:
                if st.button("Resend", key="btn_chatgpt_resend", use_container_width=True, disabled=not backend_online):
                    if not ver_email.strip():
                        st.error("Enter email to resend.")
                    else:
                        with st.spinner("Sending OTP..."):
                            res = api_request_verification_otp(ver_email)
                        if res["success"]:
                            otp_hint = res["data"].get("otp", "")
                            st.info(f"OTP generated! ({otp_hint})" if otp_hint else "OTP sent!")
                        else:
                            st.error(f"❌ {res['error']}")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("Back to Log in", key="btn_verify_back", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

        # -----------------------------------------------------
        # VIEW 4: CHATGPT FORGOT PASSWORD
        # -----------------------------------------------------
        elif auth_mode == "forgot":
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; margin-bottom: 22px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 26px; color: #ffffff; margin-bottom: 12px;">
                        🔑
                    </div>
                    <h1 style="color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Reset password</h1>
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Enter your email to receive a reset code</div>
                </div>
            """, unsafe_allow_html=True)

            fgt_email = st.text_input("Email address", key="auth_fgt_email", placeholder="name@example.com")

            if st.button("Send reset code", key="btn_send_reset_otp", use_container_width=True, disabled=not backend_online):
                if not fgt_email.strip():
                    st.error("Please enter your registered email.")
                else:
                    with st.spinner("Requesting reset OTP..."):
                        res = api_forgot_password(fgt_email)
                    if res["success"]:
                        otp_hint = res["data"].get("otp", "")
                        st.info(f"Reset OTP: {otp_hint}" if otp_hint else "Reset OTP generated!")
                    else:
                        st.error(f"❌ {res['error']}")

            st.markdown("<div style='margin: 14px 0; border-top: 1px solid #232733;'></div>", unsafe_allow_html=True)
            rst_otp = st.text_input("Reset code (OTP)", key="auth_rst_otp", placeholder="6-digit code")
            rst_new_pw = st.text_input("New password", type="password", key="auth_rst_new_pw", placeholder="New password (min 6 chars)")

            if st.button("Set new password", key="btn_do_reset_pw", type="primary", use_container_width=True, disabled=not backend_online):
                if not fgt_email.strip() or not rst_otp.strip() or len(rst_new_pw) < 6:
                    st.error("Please provide email, OTP, and valid new password.")
                else:
                    with st.spinner("Resetting password..."):
                        res = api_reset_password(fgt_email, rst_otp, rst_new_pw)
                    if res["success"]:
                        st.success("✅ Password reset! You can now log in.")
                        st.session_state.auth_mode = "login"
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(f"❌ {res['error']}")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("Back to Log in", key="btn_forgot_back", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

    # End execution of unauthenticated state
    st.stop()


# -------------------------------------------------------------
# 8. AUTHENTICATED USER INTERFACE & SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    # High-Tech Brand Header
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
            <span style="font-size: 1.8rem;">⚡</span>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; color: #00f2fe; letter-spacing: 1px;">NEXUS CORE</div>
                <div style="font-size: 0.72rem; color: #64748b; font-family: monospace;">NEURAL CHAT ENGINE v2.0</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Backend Online / Offline Status Badge
    if backend_online:
        st.markdown(f'<div class="tech-badge-green">● SYSTEM ONLINE</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="tech-badge-red">● BACKEND OFFLINE</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # User Profile Snippet in Sidebar
    user_display_name = f"{st.session_state.user_first_name} {st.session_state.user_surname}".strip() or st.session_state.user_full_name or "Explorer"
    if avatar_base64_src:
        avatar_markup = f'<img src="{avatar_base64_src}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 2px solid #00f2fe; box-shadow: 0 0 10px rgba(0,242,254,0.3);">'
    else:
        avatar_markup = '<div style="width: 42px; height: 42px; border-radius: 50%; background: #131d2e; border: 1.5px solid #00f2fe; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">👨‍💻</div>'

    verified_badge = '<span class="tech-badge-green" style="font-size: 0.68rem; padding: 1px 5px;">VERIFIED</span>' if st.session_state.is_email_verified else '<span class="tech-badge-red" style="font-size: 0.68rem; padding: 1px 5px;">UNVERIFIED</span>'

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 8px;">
            {avatar_markup}
            <div style="overflow: hidden; width: 100%;">
                <div style="font-weight: 700; font-size: 0.92rem; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_display_name}</div>
                <div style="font-size: 0.70rem; color: #94a3b8; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.user_email}</div>
                <div style="margin-top: 3px;">{verified_badge}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Logout Button
    if st.button("🚪 Sign Out", key="sidebar_logout_btn", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.auth_token = None
        st.session_state.user_id = ""
        st.session_state.user_email = ""
        st.session_state.user_full_name = ""
        st.session_state.current_chat_id = None
        st.session_state.chats = None
        st.session_state.messages = []
        st.toast("Signed out successfully", icon="👋")
        st.rerun()

    # Model Selection
    st.markdown("<span style='font-size: 0.8rem; font-weight: 600; color: #94a3b8; font-family: monospace;'>⚡ NEURAL MODEL</span>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "OpenRouter Model:",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 1,
        label_visibility="collapsed"
    )
    st.session_state.selected_model = selected_model

    st.divider()

    # 📜 OLD CHATS IN CLEAN TEXT FORMAT
    col_hist_title, col_refresh = st.columns([0.78, 0.22])
    with col_hist_title:
        st.markdown("<span style='font-size: 0.82rem; font-weight: 700; color: #38bdf8; letter-spacing: 0.8px;'>📁 CHAT HISTORY (TEXT FORMAT)</span>", unsafe_allow_html=True)
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

                # Render Old Chat in Text Format
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

    # Context Memory Info
    st.divider()
    st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e293b; border-left: 3px solid #00f2fe; padding: 10px 12px; border-radius: 6px; font-size: 0.78rem; color: #94a3b8; font-family: monospace;">
            🧠 <strong>NEURAL MEMORY: ACTIVE</strong><br>
            Buffers last 10 dialog turns seamlessly.
        </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 9. Top Navigation Bar (Header)
# -------------------------------------------------------------
top_col1, top_col2, top_col3 = st.columns([0.22, 0.48, 0.30])

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
    col_user_pill, col_menu_btn = st.columns([0.55, 0.45])
    
    with col_user_pill:
        if avatar_base64_src:
            small_pic = f'<img src="{avatar_base64_src}" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1.5px solid #00f2fe; vertical-align: middle; margin-right: 6px;">'
        else:
            small_pic = '<span style="font-size: 1.1rem; vertical-align: middle; margin-right: 6px;">👨‍💻</span>'

        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; height: 42px; overflow: hidden;">
                {small_pic}
                <span style="font-size: 0.85rem; font-weight: 700; color: #f1f5f9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95px;">
                    {st.session_state.user_first_name}
                </span>
            </div>
        """, unsafe_allow_html=True)

    with col_menu_btn:
        with st.popover("⋮  Menu", help="Settings & User Profile", use_container_width=True):
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.25rem;">⚙️</span>
                    <span style="font-weight: 800; font-size: 1.1rem; color: #00f2fe; letter-spacing: 0.5px;">SETTINGS & PROFILE</span>
                </div>
            """, unsafe_allow_html=True)

            tab_profile, tab_system = st.tabs(["👤 User Profile", "⚡ Preferences"])

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
                        if uploaded_photo is not None:
                            photo_data = uploaded_photo.read()
                            with open(USER_AVATAR_FILE, "wb") as pf:
                                pf.write(photo_data)

                        st.session_state.user_first_name = edit_first_name.strip() or "User"
                        st.session_state.user_surname = edit_surname.strip()
                        st.session_state.user_gender = edit_gender

                        save_stored_profile({
                            "first_name": st.session_state.user_first_name,
                            "surname": st.session_state.user_surname,
                            "gender": st.session_state.user_gender
                        })

                        st.toast("Profile updated successfully! ✅", icon="💾")
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
                st.markdown("<span style='font-size: 0.82rem; font-weight: 600; color: #94a3b8;'>ACTIVE NEURAL MODEL</span>", unsafe_allow_html=True)
                menu_model = st.selectbox(
                    "Select Model:",
                    options=AVAILABLE_MODELS,
                    index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 1,
                    key="menu_model_select"
                )
                if menu_model != st.session_state.selected_model:
                    st.session_state.selected_model = menu_model
                    st.rerun()

                st.markdown("---")
                st.markdown(f"""
                    <div style="font-size: 0.78rem; color: #64748b; font-family: monospace; line-height: 1.6;">
                        • Server: <span style="color: #00f2fe;">{API_BASE_URL}</span><br>
                        • Status: <span style="color: {'#10b981' if backend_online else '#f87171'};">{'CONNECTED' if backend_online else 'DISCONNECTED'}</span><br>
                        • User ID: <span style="color: #38bdf8;">{st.session_state.user_id}</span><br>
                        • Email: <span style="color: #94a3b8;">{st.session_state.user_email}</span>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


# -------------------------------------------------------------
# 10. Main Chat Screen (Hero Screen vs Active Chat)
# -------------------------------------------------------------
if not st.session_state.current_chat_id:
    # HERO SCREEN
    st.markdown(f"""
        <div style="text-align: center; padding: 35px 20px 20px 20px;">
            <div style="display: inline-block; width: 70px; height: 70px; line-height: 70px; border-radius: 50%; background: radial-gradient(circle, rgba(0,242,254,0.2) 0%, rgba(0,0,0,0) 70%); border: 1px solid #00f2fe; font-size: 2.2rem; box-shadow: 0 0 25px rgba(0, 242, 254, 0.35); margin-bottom: 15px;">
                ⚡
            </div>
            <h1 style="color: #ffffff; font-weight: 800; font-size: 2.4rem; margin: 0; letter-spacing: -0.5px;">
                NEXUS AI <span style="color: #00f2fe;">ASSISTANT</span>
            </h1>
            <p style="color: #94a3b8; font-size: 1.05rem; max-width: 600px; margin: 12px auto 25px auto;">
                Welcome back, <strong style="color: #f8fafc;">{user_display_name}</strong>! Ready for next-generation AI conversations.
            </p>
            <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                <span class="tech-badge-cyan">MODEL: {st.session_state.selected_model}</span>
                <span class="tech-badge-green">STATUS: READY</span>
                <span class="tech-badge-cyan">SESSION: {st.session_state.user_id[:8]}...</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    center_c1, center_c2, center_c3 = st.columns([0.22, 0.56, 0.22])
    with center_c2:
        st.markdown("""
            <div style="background: rgba(14, 20, 34, 0.7); border: 1px dashed #23354e; border-radius: 12px; padding: 25px 20px; text-align: center; margin-bottom: 25px;">
                <div style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 15px;">
                    Start fresh or pick an archived conversation from the sidebar!
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 INITIATE NEW CONVERSATION", key="hero_start_btn", type="primary", use_container_width=True, disabled=not backend_online):
            new_chat_res = create_new_chat(st.session_state.user_id)
            if new_chat_res:
                st.session_state.current_chat_id = new_chat_res["chat_id"]
                st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")
                st.session_state.messages = []
                st.session_state.chats = None
                st.rerun()

else:
    # ACTIVE CHAT SESSION VIEW
    short_session_id = st.session_state.current_chat_id[-8:]

    st.markdown(f"""
        <div class="tech-header-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="tech-title">
                        <span>⚡</span> {st.session_state.current_chat_title}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; font-family: monospace; margin-top: 5px;">
                        SESSION: <span style="color: #00f2fe;">#{short_session_id}</span> &nbsp;|&nbsp; MODEL: <span style="color: #cbd5e1;">{st.session_state.selected_model}</span>
                    </div>
                </div>
                <div>
                    <span class="tech-badge-green">● LIVE CONTEXT</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        avatar_icon = user_avatar_target if role == "user" else "⚡"
        
        with st.chat_message(role, avatar=avatar_icon):
            st.markdown(content)

    user_input = st.chat_input("Ask NEXUS anything (Tech query, code, reasoning)...", disabled=not backend_online)

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
                with st.spinner("⚡ Neural Core processing query..."):
                    ai_reply = send_chat_message(
                        chat_id=st.session_state.current_chat_id,
                        user_id=st.session_state.user_id,
                        message=clean_input,
                        model_name=st.session_state.selected_model
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
