import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api.routes import router as api_router
from .config import APP_NAME, APP_VERSION

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered README generator for GitHub repositories",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    """
    Root endpoint
    """
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": "AI-powered README generator for GitHub repositories",
        "endpoints": {
            "generate": "/api/generate",
            "health": "/api/health",
        }
    }

if __name__ == "__main__":
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
