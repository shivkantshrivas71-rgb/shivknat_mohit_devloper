"""
=============================================================================
Project: chatBOT_new
Description: FastAPI Authentication System with MongoDB backend
Endpoints:
  - POST /api/v1/auth/register : Register user with valid name, email & password
  - POST /api/v1/auth/login    : Authenticate user & return JWT Token
  - GET  /                     : Service status & information
  - GET  /health               : Health check (FastAPI + MongoDB)
  - GET  /docs                 : Interactive Swagger UI documentation
=============================================================================
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    # Start the server locally on port 8000 with auto-reload enabled
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
