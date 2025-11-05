"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.upload.routes import router as upload_router
from src.api.results import router as results_router

app = FastAPI(
    title="Resume Analyzer API",
    description="API for analyzing and validating resumes",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload_router, prefix="/api/v1/parse", tags=["Upload"])
app.include_router(results_router, prefix="/api/v1", tags=["Results"])


@app.get("/")
def root():
    """
    Root endpoint for the API
    Returns a status message with version info.
    """
    return {"message": "Resume Analyzer API", "version": "1.0.0", "status": "running"}


@app.get("/api/v1/health")
def health():
    """
    Health check endpoint
    Returns API health status.
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    Logs module load confirmation during server startup.
    """
    print("Section detector module loaded successfully")
