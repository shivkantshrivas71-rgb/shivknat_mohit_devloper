# ChatBOT User API (FastAPI + MongoDB)

Simple, clean and beginner-friendly user authentication system.

---

## 📁 Project Files

```text
chatBOT1_new/
├── main.py          # FastAPI App & Endpoints (/user/register, /user/login)
├── auth.py          # Password Hash & Token Generator Helpers
├── database.py      # MongoDB Connection
├── models.py        # Pydantic Schemas (UserRegister, UserLogin)
├── .env             # MongoDB URL & Secret Key
├── requirements.txt # Project Dependencies
└── venv/            # Virtual Environment
```

---

## 🚀 How to Run

1. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Run Server**:
   ```bash
   python main.py
   ```

3. **Open Interactive Docs**:
   - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 User APIs

### 1. User Register
- **Endpoint**: `POST http://127.0.0.1:8000/user/register`
- **Request Body**:
  ```json
  {
    "name": "Alex",
    "email": "alex@example.com",
    "password": "Password123"
  }
  ```

---

### 2. User Login
- **Endpoint**: `POST http://127.0.0.1:8000/user/login`
- **Request Body**:
  ```json
  {
    "email": "alex@example.com",
    "password": "Password123"
  }
  ```
