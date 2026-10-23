import streamlit as st
import requests
import time
import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional

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
        background-color: #0f182b !important;
        border-color: #1e355b !important;
    }

    /* 6. Buttons Styling */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #070a10 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.3) !important;
        letter-spacing: 0.5px;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #101726 !important;
        color: #cbd5e1 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        border-color: #00f2fe !important;
        color: #00f2fe !important;
        box-shadow: 0 0 8px rgba(0, 242, 254, 0.2) !important;
    }

    /* 7. Top-Right 3-Dots Popover Styling */
    div[data-testid="stPopover"] > button {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        color: #00f2fe !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.15) !important;
        transition: all 0.2s ease !important;
        font-size: 1rem !important;
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
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Persistent User Profile Storage & Configuration
# -------------------------------------------------------------
API_BASE_URL = "http://localhost:8000"
PROFILE_DATA_FILE = "user_profile.json"
USER_AVATAR_FILE = "user_avatar.png"

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

if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"

if "user_first_name" not in st.session_state:
    st.session_state.user_first_name = default_profile.get("first_name", "Shivkant")

if "user_surname" not in st.session_state:
    st.session_state.user_surname = default_profile.get("surname", "Shrivas")

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
# 4. Helper Functions (Optimized with In-Memory Caching)
# -------------------------------------------------------------
def check_backend_health() -> bool:
    """Check backend health with a cached timestamp to prevent rerun lag."""
    now = time.time()
    last_check = st.session_state.get("_backend_last_checked", 0)
    last_status = st.session_state.get("_backend_status", False)
    
    if (now - last_check < 8.0) and ("_backend_status" in st.session_state):
        return last_status

    try:
        resp = requests.get(f"{API_BASE_URL}/", timeout=1.5)
        is_healthy = (resp.status_code == 200)
    except Exception:
        is_healthy = False

    st.session_state["_backend_last_checked"] = now
    st.session_state["_backend_status"] = is_healthy
    return is_healthy


def fetch_user_chats(user_id: str, force_reload: bool = False) -> List[Dict]:
    """Fetch user chats with caching in session state for fast navigation."""
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
    try:
        resp = requests.post(
            f"{API_BASE_URL}/chats/new",
            json={"user_id": user_id.strip()},
            timeout=4.0
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
        resp = requests.get(f"{API_BASE_URL}/chats/{chat_id.strip()}/messages", timeout=4.0)
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
        resp = requests.post(f"{API_BASE_URL}/chats/send", json=payload, timeout=60.0)
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
# 5. Profile Picture & Avatar Handling
# -------------------------------------------------------------
has_custom_avatar = os.path.exists(USER_AVATAR_FILE)
user_avatar_target = USER_AVATAR_FILE if has_custom_avatar else "👨‍💻"

# Generate base64 string for HTML previews if image exists
avatar_base64_src = ""
if has_custom_avatar:
    try:
        with open(USER_AVATAR_FILE, "rb") as f:
            encoded_bytes = base64.b64encode(f.read()).decode("utf-8")
            avatar_base64_src = f"data:image/png;base64,{encoded_bytes}"
    except Exception:
        avatar_base64_src = ""

# -------------------------------------------------------------
# 6. Sidebar Layout & Controls
# -------------------------------------------------------------
backend_online = check_backend_health()

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
        st.markdown('<div class="tech-badge-green">● SYSTEM ONLINE (PORT 8000)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="tech-badge-cyan" style="color: #f87171; border-color: #f87171;">● BACKEND OFFLINE</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # User Profile Snippet in Sidebar
    user_full_name = f"{st.session_state.user_first_name} {st.session_state.user_surname}".strip()
    if avatar_base64_src:
        avatar_markup = f'<img src="{avatar_base64_src}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 2px solid #00f2fe; box-shadow: 0 0 10px rgba(0,242,254,0.3);">'
    else:
        avatar_markup = '<div style="width: 42px; height: 42px; border-radius: 50%; background: #131d2e; border: 1.5px solid #00f2fe; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">👨‍💻</div>'

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 12px;">
            {avatar_markup}
            <div style="overflow: hidden;">
                <div style="font-weight: 700; font-size: 0.92rem; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_full_name}</div>
                <div style="font-size: 0.72rem; color: #94a3b8; font-family: monospace;">Gender: {st.session_state.user_gender}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # User Session ID input
    with st.expander("🔑 Session ID Config", expanded=False):
        new_user_id = st.text_input(
            "User ID:",
            value=st.session_state.user_id,
            key="user_id_field"
        )
        if new_user_id.strip() and new_user_id.strip() != st.session_state.user_id:
            st.session_state.user_id = new_user_id.strip()
            st.session_state.current_chat_id = None
            st.session_state.chats = None
            st.session_state.messages = []
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
# 7. Main Window: Top Bar with CENTER New Chat & TOP-RIGHT 3-Dots Settings
# -------------------------------------------------------------

top_col1, top_col2, top_col3 = st.columns([0.22, 0.48, 0.30])

with top_col1:
    # Left brand badge
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; height: 42px;">
            <span style="color: #00f2fe; font-size: 1.3rem;">⚡</span>
            <span style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.5px; color: #f8fafc;">NEXUS // AI</span>
        </div>
    """, unsafe_allow_html=True)

with top_col2:
    # CENTERED "NEW CHAT" BUTTON
    if st.button("⚡ + NEW CHAT", key="center_new_chat_btn", type="primary", use_container_width=True, disabled=not backend_online):
        new_chat_res = create_new_chat(st.session_state.user_id)
        if new_chat_res:
            st.session_state.current_chat_id = new_chat_res["chat_id"]
            st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")
            st.session_state.messages = []
            st.session_state.chats = None
            st.rerun()

with top_col3:
    # TOP-RIGHT CORNER: 3-DOTS MENU (⋮) WITH SETTINGS & USER PROFILE
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
        # The 3-Dots Button with Popover Menu
        with st.popover("⋮  Menu", help="Settings & User Profile", use_container_width=True):
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.25rem;">⚙️</span>
                    <span style="font-weight: 800; font-size: 1.1rem; color: #00f2fe; letter-spacing: 0.5px;">SETTINGS & PROFILE</span>
                </div>
            """, unsafe_allow_html=True)

            tab_profile, tab_system = st.tabs(["👤 User Profile", "⚡ Preferences"])

            # ---------------------------------------------------------
            # TAB 1: USER PROFILE (Name, Surname, Gender, Profile Photo)
            # ---------------------------------------------------------
            with tab_profile:
                # 1. Profile Photo Preview & Upload
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

                # 2. First Name Input
                edit_first_name = st.text_input(
                    "First Name (नाम):",
                    value=st.session_state.user_first_name,
                    key="input_first_name"
                )

                # 3. Surname / Last Name Input
                edit_surname = st.text_input(
                    "Surname / Last Name (उपनाम):",
                    value=st.session_state.user_surname,
                    key="input_surname"
                )

                # 4. Gender Selection
                gender_choices = ["Male", "Female", "Other", "Prefer not to say"]
                curr_gender_idx = gender_choices.index(st.session_state.user_gender) if st.session_state.user_gender in gender_choices else 0
                edit_gender = st.selectbox(
                    "Gender (लिंग):",
                    options=gender_choices,
                    index=curr_gender_idx,
                    key="input_gender"
                )

                col_save, col_clear = st.columns([0.65, 0.35])
                with col_save:
                    if st.button("💾 Save Profile", key="btn_save_user_profile", type="primary", use_container_width=True):
                        # Save uploaded photo if new file selected
                        if uploaded_photo is not None:
                            photo_data = uploaded_photo.read()
                            with open(USER_AVATAR_FILE, "wb") as pf:
                                pf.write(photo_data)

                        st.session_state.user_first_name = edit_first_name.strip() or "User"
                        st.session_state.user_surname = edit_surname.strip()
                        st.session_state.user_gender = edit_gender

                        # Persist to JSON
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

            # ---------------------------------------------------------
            # TAB 2: AI & SYSTEM PREFERENCES
            # ---------------------------------------------------------
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
                        • Memory Buffer: <span style="color: #f1f5f9;">Last 10 turns</span>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 8. Main Screen (Welcome Hero vs Active Conversation)
# -------------------------------------------------------------

if not st.session_state.current_chat_id:
    # =========================================================
    # WELCOME / HERO SCREEN (CENTERED & MODERN TECH AESTHETIC)
    # =========================================================
    st.markdown(f"""
        <div style="text-align: center; padding: 35px 20px 20px 20px;">
            <div style="display: inline-block; width: 70px; height: 70px; line-height: 70px; border-radius: 50%; background: radial-gradient(circle, rgba(0,242,254,0.2) 0%, rgba(0,0,0,0) 70%); border: 1px solid #00f2fe; font-size: 2.2rem; box-shadow: 0 0 25px rgba(0, 242, 254, 0.35); margin-bottom: 15px;">
                ⚡
            </div>
            <h1 style="color: #ffffff; font-weight: 800; font-size: 2.4rem; margin: 0; letter-spacing: -0.5px;">
                NEXUS AI <span style="color: #00f2fe;">ASSISTANT</span>
            </h1>
            <p style="color: #94a3b8; font-size: 1.05rem; max-width: 600px; margin: 12px auto 25px auto;">
                Welcome back, <strong style="color: #f8fafc;">{user_full_name}</strong>! Ready for next-generation AI conversations.
            </p>
            <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
                <span class="tech-badge-cyan">MODEL: {st.session_state.selected_model}</span>
                <span class="tech-badge-green">STATUS: READY</span>
                <span class="tech-badge-cyan">USER: {st.session_state.user_id}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Large Center Action Card
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
    # =========================================================
    # ACTIVE CHAT SESSION VIEW
    # =========================================================
    short_session_id = st.session_state.current_chat_id[-8:]

    # Header Card with Active Conversation Details
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

    # Render Existing Messages with Tech Avatars (Uses custom user photo if uploaded)
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        avatar_icon = user_avatar_target if role == "user" else "⚡"
        
        with st.chat_message(role, avatar=avatar_icon):
            st.markdown(content)

    # Chat Input Box
    user_input = st.chat_input("Ask NEXUS anything (Tech query, code, reasoning)...", disabled=not backend_online)

    if user_input:
        clean_input = user_input.strip()
        if clean_input:
            # 1. Instantly display user message
            st.session_state.messages.append({
                "role": "user",
                "content": clean_input
            })
            with st.chat_message("user", avatar=user_avatar_target):
                st.markdown(clean_input)

            # 2. Get AI Response with Tech Spinner
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

                    # Update chat title if changed
                    st.session_state.chats = None
                    refreshed = fetch_user_chats(st.session_state.user_id, force_reload=True)
                    for c in refreshed:
                        if c["chat_id"] == st.session_state.current_chat_id:
                            st.session_state.current_chat_title = c.get("title", st.session_state.current_chat_title)
                            break
                    st.rerun()
