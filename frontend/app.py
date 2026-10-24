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
    /* 1. Prevent Streamlit brightness fading/dimming during reruns & Authentic ChatGPT Dark Theme */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #212121 !important;
        background: #212121 !important;
        color: #ececec !important;
        opacity: 1 !important;
        transition: none !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }
    
    div[data-testid="stAppViewContainer"] > section {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
        background-color: #212121 !important;
    }

    div[data-st-app-view="true"], div[data-testid="stMain"], div[data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
        animation: none !important;
        background-color: #212121 !important;
    }

    /* Hide the top-right blinking reload spinner indicator */
    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. Sidebar ChatGPT Dark Styling (#171717) */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #2f2f2f !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ececec !important;
        font-weight: 600 !important;
    }

    /* 3. Real ChatGPT Message Styling */
    /* User Message Bubble (#2f2f2f) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #2f2f2f !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        padding: 12px 18px !important;
        margin-bottom: 12px !important;
        color: #ececec !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }

    /* Assistant Reply (Clean transparent stream) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 4px !important;
        margin-bottom: 16px !important;
        color: #ececec !important;
    }

    /* 4. Chat History Item in Sidebar (#171717 with subtle hover) */
    .history-card {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 4px;
        transition: all 0.12s ease-in-out;
    }
    
    .history-card:hover {
        background-color: #212121;
        border-color: #2f2f2f;
    }

    .history-card-active {
        background-color: #212121 !important;
        border: 1px solid #383838 !important;
    }

    .history-title {
        color: #ececec;
        font-size: 0.88rem;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }

    .history-meta {
        font-size: 0.72rem;
        color: #8e8ea0;
        margin-top: 2px;
        display: flex;
        justify-content: space-between;
    }

    /* 5. Minimalist Buttons */
    .stButton > button {
        background-color: #212121 !important;
        color: #ececec !important;
        border: 1px solid #2f2f2f !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background-color: #2f2f2f !important;
        border-color: #424242 !important;
        color: #ffffff !important;
    }

    /* ChatGPT Accent Button (Green #10a37f) */
    .stButton > button[kind="primary"] {
        background: #10a37f !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 10px rgba(16, 163, 127, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1a7f64 !important;
        box-shadow: 0 4px 14px rgba(16, 163, 127, 0.45) !important;
    }

    /* Settings Popover */
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        border: 1px solid #2f2f2f !important;
        border-radius: 8px !important;
        color: #ececec !important;
        padding: 5px 12px !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #2f2f2f !important;
        border-color: #424242 !important;
    }

    div[data-testid="stPopoverBody"] {
        background-color: #171717 !important;
        border: 1px solid #2f2f2f !important;
        border-radius: 14px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7) !important;
        color: #ececec !important;
        padding: 18px !important;
    }

    /* 6. Floating Input Bar (ChatGPT Pill Shape) */
    .stChatFloatingInputContainer {
        bottom: 15px;
        background: transparent !important;
    }

    [data-testid="stChatInput"] {
        background-color: #2f2f2f !important;
        border-radius: 26px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #ececec !important;
        background: transparent !important;
    }

    /* ChatGPT Auth Screen Styling */
    .chatgpt-auth-card {
        background: #171717;
        border: 1px solid #2f2f2f;
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
    }
    .chatgpt-auth-desc {
        color: #8e8ea0;
        font-size: 0.90rem;
        text-align: center;
        margin-bottom: 22px;
    }

    /* Quick Prompt Cards */
    .prompt-chip {
        background: #212121;
        border: 1px solid #2f2f2f;
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: all 0.12s ease-in-out;
    }
    .prompt-chip:hover {
        background: #2a2a2a;
        border-color: rgba(255, 255, 255, 0.2);
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
        # Subtle Backend Offline Notice if needed (Clean chip, no ugly banner)
        if not backend_online:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 14px;">
                    <span style="display: inline-block; background: rgba(239, 68, 68, 0.12); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.25); padding: 4px 12px; border-radius: 12px; font-size: 0.82rem;">
                        ● Backend server is offline ({API_BASE_URL})
                    </span>
                </div>
            """, unsafe_allow_html=True)

        auth_mode = st.session_state.get("auth_mode", "welcome")

        # -----------------------------------------------------
        # VIEW 0: CHATGPT WELCOME / GET STARTED (LANDING)
        # -----------------------------------------------------
        if auth_mode == "welcome":
            st.markdown("""
                <div style="text-align: center; margin-top: 40px; margin-bottom: 24px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 28px; color: #ffffff; margin-bottom: 16px;">
                        ⚡
                    </div>
                    <h1 style="color: #ffffff; font-size: 2.0rem; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.5px;">Welcome to ChatGPT</h1>
                    <div style="color: #8e8ea0; font-size: 0.95rem;">Log in with your account or sign up to get started</div>
                </div>
            """, unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Log in", key="btn_welcome_login", type="primary", use_container_width=True, disabled=not backend_online):
                    st.session_state.auth_mode = "login"
                    st.rerun()
            with col_btn2:
                if st.button("Sign up", key="btn_welcome_signup", use_container_width=True, disabled=not backend_online):
                    st.session_state.auth_mode = "register"
                    st.rerun()

            st.markdown("<div style='margin-top: 18px; border-top: 1px solid #2f2f2f; padding-top: 16px;'></div>", unsafe_allow_html=True)
            if st.button("Continue as Guest", key="btn_guest_welcome", use_container_width=True):
                st.session_state.is_authenticated = True
                st.session_state.user_id = "guest_user"
                st.session_state.user_email = "guest@chatgpt.local"
                st.session_state.user_full_name = "Guest Explorer"
                st.session_state.user_first_name = "Guest"
                st.session_state.user_surname = "User"
                st.session_state.is_email_verified = True
                st.rerun()

        # -----------------------------------------------------
        # VIEW 1: CHATGPT LOGIN (EXISTING USERS)
        # -----------------------------------------------------
        elif auth_mode == "login":
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; margin-bottom: 22px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 26px; color: #ffffff; margin-bottom: 12px;">
                        ⚡
                    </div>
                    <h1 style="color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Welcome back</h1>
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Enter your email and password to log in</div>
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

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("← Back to home", key="btn_login_back_home", use_container_width=True):
                st.session_state.auth_mode = "welcome"
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
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Enter your details to get started with ChatGPT</div>
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
                    with st.spinner("Creating account & generating verification OTP..."):
                        res = api_user_register(reg_name, reg_email, reg_password)
                    if res["success"]:
                        st.session_state._last_registered_email = reg_email.strip()
                        st.session_state.auth_mode = "verify"
                        st.success("🎉 Account created! Please enter the 6-digit OTP code to verify your email.")
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

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("← Back to home", key="btn_register_back_home", use_container_width=True):
                st.session_state.auth_mode = "welcome"
                st.rerun()

        # -----------------------------------------------------
        # VIEW 3: CHATGPT VERIFY EMAIL OTP
        # -----------------------------------------------------
        elif auth_mode == "verify":
            st.markdown("""
                <div style="text-align: center; margin-top: 30px; margin-bottom: 22px;">
                    <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: 50%; background: #10a37f; box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4); font-size: 26px; color: #ffffff; margin-bottom: 12px;">
                        🛡️
                    </div>
                    <h1 style="color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px;">Verify your email</h1>
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Enter the 6-digit verification code sent to your email</div>
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
                            st.success("✅ Email verified! Please log in with your credentials to start chatting.")
                            st.session_state.auth_mode = "login"
                            time.sleep(1.2)
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
                            st.info(f"OTP: {otp_hint}" if otp_hint else "New OTP sent!")
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
                    <div style="color: #8e8ea0; font-size: 0.90rem;">Enter your email to receive a password reset code</div>
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

            st.markdown("<div style='margin: 14px 0; border-top: 1px solid #2f2f2f;'></div>", unsafe_allow_html=True)
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
    # 1. ChatGPT + New Chat Button at top of Sidebar
    if st.button("＋  New chat", key="sidebar_new_chat_top", use_container_width=True, disabled=not backend_online):
        st.session_state.current_chat_id = None
        st.session_state.current_chat_title = "New Conversation"
        st.session_state.messages = []
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Model Selector
    selected_model = st.selectbox(
        "Model:",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 1,
        label_visibility="collapsed"
    )
    st.session_state.selected_model = selected_model

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 📜 Chat History
    col_hist_title, col_refresh = st.columns([0.80, 0.20])
    with col_hist_title:
        st.markdown("<span style='font-size: 0.78rem; font-weight: 600; color: #8e8ea0; letter-spacing: 0.5px;'>RECENT CHATS</span>", unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄", key="refresh_chats_btn", help="Refresh"):
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

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.divider()
    u_c1, u_c2 = st.columns([0.72, 0.28])
    with u_c1:
        st.markdown(f"<div style='font-size: 0.86rem; font-weight: 600; color: #ececec; padding-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>👤 {st.session_state.user_first_name}</div>", unsafe_allow_html=True)
    with u_c2:
        if st.button("Log out", key="sidebar_logout_btn", help="Sign out of account", use_container_width=True):
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
# 9. Top Navigation Bar (Header)
# -------------------------------------------------------------
top_col1, top_col2, top_col3 = st.columns([0.25, 0.45, 0.30])

with top_col1:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; height: 42px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: #10a37f; font-size: 14px; color: #ffffff;">⚡</span>
            <span style="font-weight: 700; font-size: 1.15rem; color: #ececec; letter-spacing: -0.3px;">ChatGPT</span>
        </div>
    """, unsafe_allow_html=True)

with top_col2:
    if st.button("＋ New chat", key="center_new_chat_btn", use_container_width=True, disabled=not backend_online):
        st.session_state.current_chat_id = None
        st.session_state.current_chat_title = "New Conversation"
        st.session_state.messages = []
        st.rerun()

with top_col3:
    col_user_pill, col_menu_btn = st.columns([0.55, 0.45])
    
    with col_user_pill:
        if avatar_base64_src:
            small_pic = f'<img src="{avatar_base64_src}" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1.5px solid #10a37f; vertical-align: middle; margin-right: 6px;">'
        else:
            small_pic = '<span style="display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #2f2f2f; font-size: 13px; margin-right: 6px;">👤</span>'

        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: flex-end; height: 42px; overflow: hidden;">
                {small_pic}
                <span style="font-size: 0.85rem; font-weight: 600; color: #ececec; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95px;">
                    {st.session_state.user_first_name}
                </span>
            </div>
        """, unsafe_allow_html=True)

    with col_menu_btn:
        with st.popover("⚙️ Settings", help="Settings & Profile", use_container_width=True):
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #ececec;">Settings</span>
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
# 10. Main Chat Screen (Authentic Real-World ChatGPT Experience)
# -------------------------------------------------------------

# If conversation is fresh (no messages yet):
if not st.session_state.messages:
    st.markdown(f"""
        <div style="text-align: center; margin: 10vh auto 3vh auto; max-width: 650px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 54px; height: 54px; border-radius: 50%; background: #2f2f2f; margin-bottom: 16px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
                <span style="font-size: 26px; color: #10a37f;">⚡</span>
            </div>
            <h1 style="color: #ececec; font-size: 2.1rem; font-weight: 600; margin: 0 0 8px 0; letter-spacing: -0.6px;">What can I help with?</h1>
            <div style="color: #8e8ea0; font-size: 0.95rem;">Ask a question, write code, analyze data, or explore any idea.</div>
        </div>
    """, unsafe_allow_html=True)

    # 4 Real ChatGPT Prompt Suggestion Cards
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("💡 Brainstorm creative ideas for a new web project", key="prompt_btn_1", use_container_width=True):
            st.session_state._injected_prompt = "Brainstorm creative ideas for a new web project"
            st.rerun()
        if st.button("🐍 Write a Python script to automate a daily task", key="prompt_btn_2", use_container_width=True):
            st.session_state._injected_prompt = "Write a Python script to automate a daily task"
            st.rerun()
    with col_p2:
        if st.button("🔍 Explain how neural networks learn in simple terms", key="prompt_btn_3", use_container_width=True):
            st.session_state._injected_prompt = "Explain how neural networks learn in simple terms"
            st.rerun()
        if st.button("🛠️ Help me debug a complex code issue or error", key="prompt_btn_4", use_container_width=True):
            st.session_state._injected_prompt = "Help me debug a complex code issue or error"
            st.rerun()

else:
    # ACTIVE CHAT SESSION VIEW
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        avatar_icon = user_avatar_target if role == "user" else "⚡"
        
        with st.chat_message(role, avatar=avatar_icon):
            st.markdown(content)

# Input Bar - Always active and ready at bottom!
injected_prompt = st.session_state.pop("_injected_prompt", None)
user_input = st.chat_input("Message ChatGPT...", disabled=not backend_online)

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

        st.session_state.messages.append({
            "role": "user",
            "content": clean_input
        })
        with st.chat_message("user", avatar=user_avatar_target):
            st.markdown(clean_input)

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("Thinking..."):
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
