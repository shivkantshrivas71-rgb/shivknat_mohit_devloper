# ChatBOT User Authentication API (FastAPI + MongoDB)

Complete and secure asynchronous user authentication and management system built with FastAPI, Motor (Async MongoDB), and JWT.

---

## ✨ Features

1. **User Registration**: Register with name, email, and password (hashed using `bcrypt`).
2. **Email Verification**:
   - `POST /user/verify-email/request` : Request or resend 6-digit verification OTP.
   - `POST /user/verify-email` : Verify OTP to mark account as email-verified.
3. **User Authentication (Login)**: Authenticates credentials and returns a secure JWT Bearer token stored in MongoDB.
4. **User Profile Management**:
   - `GET /user/profile` : View authenticated user's profile details.
   - `PUT /user/profile` : Update user profile (e.g., full name).
5. **Password Reset Flow**:
   - `POST /user/forgot-password` : Generate 6-digit OTP valid for 10 minutes.
   - `POST /user/reset-password` : Verify OTP, update password, and invalidate existing sessions.

---

## 📁 Project Structure

```text
chatBOT1_new/
├── app.py           # Streamlit Web UI Frontend application
├── main.py          # FastAPI application, route handlers, and configuration
├── auth.py          # Password hashing, JWT token management, and auth dependencies
├── database.py      # Asynchronous MongoDB connection using Motor
├── models.py        # Pydantic data schemas for authentication requests & responses
├── router/          # Modular routing directory
│   ├── __init__.py
│   ├── chat_router.py  # Chat session and messaging endpoints
│   └── schemas.py      # Chat Pydantic request/response schemas
├── services/        # External service integrations
│   ├── __init__.py
│   └── llm_service.py  # OpenRouter LLM service caller
├── .env             # Environment configuration (MongoDB, Secret Key, OpenRouter Key)
├── requirements.txt # Project dependencies
└── README.md        # Project documentation
```

---

## 🚀 Getting Started

### 1. Configure `.env`
Ensure your [chatBOT1_new/.env](file:///d:/chotebotproject0001/chatBOT1_new/.env) contains:
```env
MONGODB_URL=mongodb+srv://...
DATABASE_NAME=chatbot_db
SECRET_KEY=your_jwt_secret
OPENROUTER_API_KEY=sk-or-v1-...
```

### 2. Start the FastAPI Backend

From the `chatBOT1_new` folder:
```bash
uvicorn main:app --reload
```

### 3. Start the Streamlit Frontend

In a separate terminal window:
```bash
streamlit run app.py
```
This opens the ChatGPT frontend interface in your browser at:
👉 **`http://localhost:8501`**

### 4. Interactive API Documentation

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** (Swagger UI)

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | API status and health check | No |
| `POST` | `/user/register` | Register new user | No |
| `POST` | `/user/verify-email/request` | Request verification OTP | No |
| `POST` | `/user/verify-email` | Confirm verification OTP | No |
| `POST` | `/user/login` | Authenticate user & receive JWT | No |
| `GET` | `/user/profile` | View current user profile | Yes (Bearer) |
| `PUT` | `/user/profile` | Update current user profile | Yes (Bearer) |
| `POST` | `/user/forgot-password` | Request password reset OTP | No |
| `POST` | `/user/reset-password` | Set new password with OTP | No |
| `POST` | `/chats/new` | Create new conversation session | No |
| `GET` | `/chats/{user_id}` | List all conversations for user | No |
| `GET` | `/chats/{chat_id}/messages` | Get message history for chat | No |
| `POST` | `/chats/send` | Send message, memory (last 10), OpenRouter AI reply | No |
| `DELETE` | `/chats/{chat_id}` | Delete chat session & messages | No |

---

## 💬 ChatGPT Chat Backend (OpenRouter)

### 1. Create a Chat
- **POST** `/chats/new`
- Payload: `{"user_id": "user_id_here"}`
- Returns: `chat_id` and default title `"New Conversation"`

### 2. Send Message with 10-Message Memory & OpenRouter Call
- **POST** `/chats/send`
- Payload:
  ```json
  {
    "chat_id": "6adb...",
    "user_id": "user_id_here",
    "message": "Explain quantum computing in simple terms",
    "model_name": "openai/gpt-3.5-turbo"
  }
  ```
- **Context Memory**: Automatically queries strictly the last 10 messages from MongoDB (`.sort("timestamp", -1).limit(10)`), restores chronological order, formats into standard OpenAI role schema, and sends request to OpenRouter.
- **Auto-Title**: Automatically updates `"New Conversation"` with the first 25 characters of the user prompt (`...`).

---

## 🔒 Authentication in Swagger UI

To test protected routes (`/user/profile`):
1. Call `POST /user/login` to get your `access_token`.
2. Click the green **Authorize** button at the top of the Swagger UI (`/docs`).
3. Paste the token into the **Value** field and click **Authorize**.
