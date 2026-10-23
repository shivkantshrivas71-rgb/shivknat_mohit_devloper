# chatBOT_new - Authentication & User Management API

A clean, modular, and production-ready authentication API built with **FastAPI** and **MongoDB** (via async Motor driver).

---

## 🚀 Features

- **User Registration**:
  - Name validation (min 2 chars)
  - Strict email validation using `email-validator` & Pydantic
  - Password length validation (min 6 chars)
  - Secure password hashing using `bcrypt`
  - Unique email indexing in MongoDB
- **User Login**:
  - Validates email and verifies hashed password
  - Generates secure **JWT (JSON Web Tokens)**
- **Modern FastAPI Lifespan**:
  - Auto-initializes MongoDB connection and creates unique indexes
  - Graceful connection cleanup on shutdown
- **Clean Architecture**:
  - Modular structure separating models, routers, utilities, and configuration
  - Centralized root `main.py` entrypoint

---

## 📁 Project Structure

```text
chatBOT1_new/
│
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # Pydantic schemas (Register, Login, Token, Response)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py             # Auth endpoints (/auth/register, /auth/login)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── security.py         # Bcrypt hashing & JWT token generation
│   ├── __init__.py
│   ├── config.py               # Environment configuration settings
│   ├── database.py             # Async MongoDB connection & indexing
│   └── main.py                 # FastAPI application factory & CORS
│
├── venv/                       # Python Virtual Environment
├── .env                        # Active environment variables
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Project dependencies
├── main.py                     # Root entrypoint to run the server
└── README.md                   # Documentation
```

---

## 🛠️ Getting Started

### 1. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

### 2. Configure Environment Variables

Edit the `.env` file if you are using MongoDB Atlas or custom MongoDB credentials:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=chatbot_db
SECRET_KEY=chatbot_super_secret_jwt_key_2026_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> **Note**: Make sure MongoDB is running locally (e.g. MongoDB Community Server) or provide a remote MongoDB Atlas URI in `MONGODB_URL`.

### 3. Run the Application

Run directly with Python:
```bash
python main.py
```

Or using Uvicorn:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The server will start at: `http://127.0.0.1:8000`  
Interactive Swagger API Documentation: `http://127.0.0.1:8000/docs`  
ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 📡 API Endpoints

### 1. Register User
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/v1/auth/register`
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "password": "SecretPassword123"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": "6718a2bc45df890123456789",
    "name": "John Doe",
    "email": "johndoe@example.com",
    "created_at": "2026-10-23T09:50:00.000Z"
  }
  ```

---

### 2. User Login
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/v1/auth/login`
- **Request Body**:
  ```json
  {
    "email": "johndoe@example.com",
    "password": "SecretPassword123"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "6718a2bc45df890123456789",
      "name": "John Doe",
      "email": "johndoe@example.com",
      "created_at": "2026-10-23T09:50:00.000Z"
    }
  }
  ```

---

### 3. Health Check
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/health`
- **Response**:
  ```json
  {
    "status": "healthy",
    "database": "connected"
  }
  ```
