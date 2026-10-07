from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analysis import router as analysis_router
from app.routes.monitoring import router as monitoring_router
from app.database.database import Base, engine
from app.models.detection import Detection
from app.config import settings


# Create database tables
Base.metadata.create_all(bind=engine)


# -------------------------------------------------------------------
# FastAPI application
# -------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="DDoS detection backend using LUCID",
    version=settings.APP_VERSION,
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Routers
# -------------------------------------------------------------------

app.include_router(analysis_router)
app.include_router(monitoring_router)


# -------------------------------------------------------------------
# Basic health check
# -------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "NetShield API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }