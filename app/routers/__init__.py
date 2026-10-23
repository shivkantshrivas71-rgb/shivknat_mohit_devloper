"""API Routers package.
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

from fastapi import APIRouter
from app.routers import auth

# Main router instance
router = APIRouter(prefix="/api/v1", tags=["API Version"])

# Register individual routers
router.include_router(auth.router)

__all__ = ["router"]

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
