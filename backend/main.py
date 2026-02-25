"""
FastAPI Main Application
"""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Local Lode API",
    description="RAG-based note search tool API",
    version="2.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Get project root
project_root = Path(__file__).resolve().parent.parent

# Mount static files (frontend)
frontend_path = project_root / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info(f"Mounted static files from {frontend_path}")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve the favicon"""
    favicon_path = frontend_path / "favicon.png"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return None


@app.get("/")
async def root():
    """Serve the frontend index.html"""
    frontend_index = project_root / "frontend" / "index.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    else:
        return {"message": "Local Lode API is running. Frontend not found."}


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info("Local Lode API Starting...")
    logger.info(f"Project root: {project_root}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Local Lode API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
