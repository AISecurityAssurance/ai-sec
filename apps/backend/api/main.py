"""
FastAPI application setup
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from api.routes import analysis, artifacts, chat, versions, stpa_sec
from api.websocket import websocket_endpoint
from api.dependencies import get_orchestrator
from storage.database import init_db
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await init_db()
    print("Database initialized")
    
    yield
    
    # Shutdown
    print("Shutting down")


app = FastAPI(
    title="Security Analysis Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    analysis.router,
    prefix="/api/analysis",
    tags=["analysis"]
)
app.include_router(
    artifacts.router,
    prefix="/api/artifacts",
    tags=["artifacts"]
)
app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["chat"]
)
app.include_router(
    versions.router,
    prefix="/api/versions",
    tags=["versions"]
)
app.include_router(
    stpa_sec.router,
    prefix="/api/stpa-sec",
    tags=["STPA-Sec"]
)

# WebSocket endpoint
app.websocket("/ws/{analysis_id}")(websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Security Analysis Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}