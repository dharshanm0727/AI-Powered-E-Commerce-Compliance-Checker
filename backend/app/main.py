import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.core.logging_config import setup_logging
from app.api.v1.api import api_router

logger = setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Production Health Check Endpoint.
    Verifies Database and API responsiveness.
    """
    try:
        # Ping Database
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check DB failure: {e}")
        db_status = "unhealthy"

    status_code = 200 if db_status == "healthy" else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "version": settings.VERSION,
            "project": settings.PROJECT_NAME
        }
    )


static_dir = os.path.join(os.path.dirname(__file__), "static")

@app.get("/", include_in_schema=False)
def read_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "Legal Metrology E-Commerce Compliance Checker API",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health",
        "status": "online"
    }


if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
