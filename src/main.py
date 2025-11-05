"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.upload.routes import router as upload_router

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


@app.get("/")
def root():
    return {"message": "Resume Analyzer API", "version": "1.0.0", "status": "running"}


@app.get("/api/v1/health")
def health():
    return {"status": "healthy"}
