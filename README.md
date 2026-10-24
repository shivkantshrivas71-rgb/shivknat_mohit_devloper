# ⚡ NEXUS AI - Real-World Client/Server Architecture

This project is organized into an industry-standard **Decoupled Architecture**:
- **Backend API Server**: High-performance asynchronous FastAPI server connected with MongoDB Atlas, JWT authentication, and OpenRouter AI.
- **Frontend Web UI**: Futuristic Cyberpunk Dark Streamlit web interface with integrated Authentication (Login, Sign-Up, OTP Verification, Password Reset) and Dynamic AI Chat sessions.

---

## 📁 Project Directory Structure

```text
chatBOT1_new/
│
├── 📂 backend/                      # 🚀 FastAPI REST API Server & Database
│   ├── main.py                     # FastAPI application & CORS configuration
│   ├── database.py                 # Async MongoDB (Motor) connection
│   ├── models.py                   # Pydantic schemas for User Auth
│   ├── auth.py                     # Password hashing, JWT token & OTP generation
│   ├── router/
│   │   ├── __init__.py
│   │   ├── chat_router.py          # /chats/new, /chats/send, /chats/{id}/messages
│   │   └── schemas.py              # Chat request and response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── llm_service.py          # OpenRouter LLM caller
│   ├── .env                        # MongoDB URL, JWT Secret, OpenRouter API Key
│   └── requirements.txt            # Backend dependencies
│
├── 📂 frontend/                     # 💻 Streamlit Cyber Web UI Client
│   ├── app.py                      # Frontend application with full Auth Gateway
│   ├── config.py                   # Dynamic API_BASE_URL (Local / Production Server)
│   ├── .streamlit/
│   │   └── config.toml             # Dark cyberpunk theme settings
│   ├── assets/                     # Custom avatars & static media
│   │   └── user_avatar.png
│   ├── user_profile.json           # Local profile cache
│   └── requirements.txt            # Frontend dependencies
│
├── ⚡ run_backend.bat               # 1-Click to run FastAPI Backend Server (Port 8000)
├── ⚡ run_frontend.bat              # 1-Click to run Streamlit Frontend UI (Port 8501)
├── 🚀 run_both.bat                  # 1-Click to launch both servers simultaneously
└── README.md                       # Project documentation
```

---

## 🌐 How Frontend & Backend Communicate (Pure API)

The Frontend **never** connects directly to MongoDB. All data flows exclusively through standard HTTP REST endpoints:

1. **Authentication Flow**:
   - `POST /user/login` ➔ Authenticates credentials and returns JWT Bearer token + User details.
   - `POST /user/register` ➔ Creates user account & generates email verification OTP.
   - `POST /user/verify-email` ➔ Validates 6-digit OTP to verify user account.
   - `POST /user/forgot-password` & `POST /user/reset-password` ➔ Secure password recovery flow.

2. **Chat & AI Messaging Flow**:
   - `GET /chats/{user_id}` ➔ Loads conversation history for the logged-in user.
   - `POST /chats/new` ➔ Initiates a new chat session.
   - `POST /chats/send` ➔ Dispatches user message, buffers history, and streams OpenRouter AI reply.
   - `DELETE /chats/{chat_id}` ➔ Deletes conversation from database.

3. **Production Server Deployment**:
   - When deploying to cloud servers (e.g. Render, AWS, DigitalOcean), set the environment variable in `frontend/.env` or system environment:
     ```env
     BACKEND_API_URL=https://your-production-api-domain.com
     ```
   - The frontend automatically routes all API calls to your live server without modifying any code!

---

## 🚀 Running the Project

### Option A: One-Click Launchers (Windows)
Double-click:
- **`run_both.bat`** ➔ Starts both Backend and Frontend in separate windows.
- Or run **`run_backend.bat`** (FastAPI at `http://localhost:8000`) and **`run_frontend.bat`** (Streamlit at `http://localhost:8501`).

### Option B: Terminal Commands

#### 1. Start Backend:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`

#### 2. Start Frontend:
```bash
cd frontend
python -m streamlit run app.py
```
- Web UI: `http://localhost:8501`
