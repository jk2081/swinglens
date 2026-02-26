from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="SwingLens API",
    description="AI-powered video coaching platform for golf academies",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
