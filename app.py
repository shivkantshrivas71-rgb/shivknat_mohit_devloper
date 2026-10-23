import streamlit as st
import requests
from typing import List, Dict, Optional

# -------------------------------------------------------------
# 1. Page Configuration & Theme
# -------------------------------------------------------------
st.set_page_config(
    page_title="ChatGPT AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, modern chat interface
st.markdown("""
<style>
    /* Styling adjustments */
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .chat-session-btn {
        margin-bottom: 5px;
    }
    .badge-info {
        background-color: #2b313e;
        color: #00d26a;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Constants & Backend URL
# -------------------------------------------------------------
API_BASE_URL = "http://localhost:8000"

AVAILABLE_MODELS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.1-8b-instruct",
    "google/gemini-flash-1.5"
]

# -------------------------------------------------------------
# 3. Session State Initialization
# -------------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Conversation"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chats" not in st.session_state:
    st.session_state.chats = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "openai/gpt-3.5-turbo"


# -------------------------------------------------------------
# 4. Backend Helper Functions
# -------------------------------------------------------------
def check_backend_health() -> bool:
    """Check if the FastAPI backend server is accessible."""
    try:
        resp = requests.get(f"{API_BASE_URL}/", timeout=2.0)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def fetch_user_chats(user_id: str) -> List[Dict]:
    """Fetch all chat sessions for the given user from FastAPI backend."""
    try:
        resp = requests.get(f"{API_BASE_URL}/chats/{user_id.strip()}", timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
        return []
    except requests.RequestException:
        return []


def create_new_chat(user_id: str) -> Optional[Dict]:
    """Create a new chat session for user."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/chats/new",
            json={"user_id": user_id.strip()},
            timeout=5.0
        )
        if resp.status_code == 201:
            return resp.json()
        return None
    except requests.RequestException as e:
        st.error(f"Error creating new chat: {str(e)}")
        return None


def fetch_chat_messages(chat_id: str) -> List[Dict]:
    """Fetch message history for a specific chat from FastAPI backend."""
    try:
        resp = requests.get(f"{API_BASE_URL}/chats/{chat_id.strip()}/messages", timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
        return []
    except requests.RequestException as e:
        st.error(f"Error loading messages: {str(e)}")
        return []


def send_chat_message(chat_id: str, user_id: str, message: str, model_name: str) -> Optional[str]:
    """Send user message and receive AI reply via FastAPI backend."""
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
    """Delete a chat session and associated messages."""
    try:
        resp = requests.delete(f"{API_BASE_URL}/chats/{chat_id.strip()}", timeout=5.0)
        return resp.status_code == 200
    except requests.RequestException:
        return False


# -------------------------------------------------------------
# 5. Sidebar Layout & Controls
# -------------------------------------------------------------
backend_online = check_backend_health()

with st.sidebar:
    st.title("🤖 ChatBot Assistant")
    
    # Backend Status Indicator
    if backend_online:
        st.caption("🟢 Backend: **Online** (`localhost:8000`)")
    else:
        st.error("🔴 Backend is Offline!\nPlease run `uvicorn main:app --reload`")

    st.divider()

    # User Session / Login Simulation
    st.subheader("👤 User Session")
    new_user_id = st.text_input(
        "Enter User ID to load conversations:",
        value=st.session_state.user_id,
        key="user_id_field"
    )
    if new_user_id != st.session_state.user_id:
        st.session_state.user_id = new_user_id.strip()
        st.session_state.current_chat_id = None
        st.session_state.messages = []
        st.rerun()

    # '+ New Chat' Action Button
    if st.button("➕ New Chat", use_container_width=True, type="primary", disabled=not backend_online):
        with st.spinner("Creating conversation..."):
            new_chat_res = create_new_chat(st.session_state.user_id)
            if new_chat_res:
                st.session_state.current_chat_id = new_chat_res["chat_id"]
                st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")
                st.session_state.messages = []
                st.rerun()

    st.divider()

    # Chat Sessions History List
    st.subheader("💬 Conversations")
    if backend_online and st.session_state.user_id:
        chat_sessions = fetch_user_chats(st.session_state.user_id)
        st.session_state.chats = chat_sessions

        if not chat_sessions:
            st.caption("No conversations found. Click **➕ New Chat** to begin!")
        else:
            for chat in chat_sessions:
                cid = chat["chat_id"]
                ctitle = chat.get("title", "New Conversation")
                is_active = (cid == st.session_state.current_chat_id)

                col_chat, col_del = st.columns([0.82, 0.18])
                with col_chat:
                    btn_label = f"👉 {ctitle}" if is_active else f"💬 {ctitle}"
                    if st.button(btn_label, key=f"chat_btn_{cid}", use_container_width=True):
                        st.session_state.current_chat_id = cid
                        st.session_state.current_chat_title = ctitle
                        with st.spinner("Loading messages..."):
                            st.session_state.messages = fetch_chat_messages(cid)
                        st.rerun()

                with col_del:
                    if st.button("🗑️", key=f"del_btn_{cid}", help="Delete this conversation"):
                        if delete_chat(cid):
                            if st.session_state.current_chat_id == cid:
                                st.session_state.current_chat_id = None
                                st.session_state.messages = []
                            st.rerun()

    st.divider()

    # Settings / Controls Section
    st.subheader("⚙️ Model Settings")
    selected_model = st.selectbox(
        "OpenRouter Model:",
        options=AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 0
    )
    st.session_state.selected_model = selected_model

    # Context Memory Info Badge
    st.markdown("""
        <div style="background-color: #1e2630; border-left: 3px solid #00d26a; padding: 8px 12px; border-radius: 4px; font-size: 0.85rem; color: #d0d7de;">
            🧠 <strong>Context Memory:</strong> Active<br>
            Strictly maintains last <strong>10 messages</strong> across turns.
        </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# 6. Main Chat Window
# -------------------------------------------------------------

# If no active chat session is selected
if not st.session_state.current_chat_id:
    st.header("👋 Welcome to AI ChatBot")
    st.write(
        f"Logged in as: **`{st.session_state.user_id}`** | Selected Model: **`{st.session_state.selected_model}`**"
    )

    st.info("👈 Select an existing conversation from the sidebar or click **➕ New Chat** to start a new session.")

    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        if st.button("🚀 Start New Conversation Now", type="primary", disabled=not backend_online):
            new_chat_res = create_new_chat(st.session_state.user_id)
            if new_chat_res:
                st.session_state.current_chat_id = new_chat_res["chat_id"]
                st.session_state.current_chat_title = new_chat_res.get("title", "New Conversation")
                st.session_state.messages = []
                st.rerun()

else:
    # Header showing active conversation title
    st.markdown(f"### 💬 {st.session_state.current_chat_title}")
    st.caption(f"Session ID: `{st.session_state.current_chat_id}` | Model: `{st.session_state.selected_model}`")

    # Render Existing Message History
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.markdown(content)

    # Chat Input Box
    user_input = st.chat_input("Type your message here...", disabled=not backend_online)

    if user_input:
        clean_input = user_input.strip()
        if clean_input:
            # 1. Instantly display user message in UI and state
            st.session_state.messages.append({
                "role": "user",
                "content": clean_input
            })
            with st.chat_message("user"):
                st.markdown(clean_input)

            # 2. Call backend to get AI reply
            with st.chat_message("assistant"):
                with st.spinner("AI is thinking..."):
                    ai_reply = send_chat_message(
                        chat_id=st.session_state.current_chat_id,
                        user_id=st.session_state.user_id,
                        message=clean_input,
                        model_name=st.session_state.selected_model
                    )

                if ai_reply:
                    st.markdown(ai_reply)
                    # 3. Append AI response to messages state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_reply
                    })

                    # Refresh chat sessions to update auto-title if it was changed
                    refreshed_chats = fetch_user_chats(st.session_state.user_id)
                    for c in refreshed_chats:
                        if c["chat_id"] == st.session_state.current_chat_id:
                            st.session_state.current_chat_title = c.get("title", st.session_state.current_chat_title)
                            break
                    st.rerun()
