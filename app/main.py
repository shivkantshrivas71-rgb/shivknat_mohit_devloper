from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, db_manager
from app.routers import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB and prepare database
    await connect_to_mongo()
    yield
    # Shutdown: Close database connections
    await close_mongo_connection()

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="FastAPI Authentication & User Management with MongoDB backend for chatBOT.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Enable CORS for all origins (can be configured for production)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Auth Router
    application.include_router(auth.router, prefix="/api/v1")

    @application.get("/", tags=["Health"])
    async def root():
        return {
            "status": "online",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs"
        }

    @application.get("/health", tags=["Health"])
    async def health_check():
        db_status = "connected" if db_manager.client is not None else "disconnected"
        return {
            "status": "healthy",
            "database": db_status
        }

    return application

app = create_application()
