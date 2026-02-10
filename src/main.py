"""
Main FastAPI application

[BUG FIX] The /download/{job_id} endpoint is updated to
call the new `get_analysis_data` service instead of
using `MOCK_ANALYSIS_REPORT`.
"""

import io
from fastapi.responses import Response
from fastapi import HTTPException

# Import your new functions from their correct modules
from src.feedback.feedback_generator import generate_pdf_report
from src.mock_data import MOCK_ANALYSIS_REPORT

import json
from src.utils.perf import time_execution
from src.upload.service import delete_and_log
# from src.database.connection import init_db  # For database initialization
from src.database.metadata_model import Base  # For table creation
from src.mock_data import MOCK_FILE_METADATA

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import Request
from fastapi.responses import RedirectResponse

# Import your new functions from their correct modules
from src.feedback.feedback_generator import generate_pdf_report

# from src.mock_data import MOCK_ANALYSIS_REPORT # <-- BUG: We don't want this
from src.api.data_service import get_analysis_data  # <-- FIX: Import the new function

# Import routers
from src.upload.routes import router as upload_router
from src.api.results import router as results_router
from src.api.compare import router as compare_router
from src.utils.error_handler import register_error_handlers


app = FastAPI(
    title="Resume Analyzer API",
    description="API for analyzing and validating resumes",
    version="1.0.0",
)

# CORS middleware (unchanged)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (unchanged)
app.include_router(upload_router, prefix="/api/v1/parse", tags=["Upload"])
app.include_router(results_router, prefix="/api/v1", tags=["Results"])
app.include_router(compare_router)


@app.get("/")
def root():
    """Root endpoint (unchanged)"""
    return {
        "message": "Resume Analyzer API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/v1/health")
def health():
    """Health check (unchanged)"""
    return {"status": "healthy"}


# --- UPDATED DOWNLOAD ENDPOINT ---


@app.get("/api/v1/download/{job_id}")
def download_report(job_id: str):
    """
    Implements the API endpoint for downloading the analysis report as PDF.
    """
    try:
        # --- THIS IS THE FIX ---
        # Get the REAL data for the job_id
        report_data = get_analysis_data(job_id)
        # ---------------------

        # Call your function from the feedback_generator
        pdf_output_bytes = generate_pdf_report(report_data)

    except Exception as e:
        # Use FastAPI's way of handling errors
        raise HTTPException(
            status_code=500, detail=f"Error generating PDF report: {str(e)}"
        )

    # Define the headers to tell the browser it's a file download
    headers = {
        "Content-Disposition": f'attachment; filename="Analysis_Report_{job_id}.pdf"'
    }

    # This is the FastAPI way to send a file
    return Response(
        content=pdf_output_bytes, media_type="application/pdf", headers=headers
    )


# --- STARTUP AND MIDDLEWARE (Unchanged) ---


@app.on_event("startup")
async def startup_event():
    """Startup event handler (unchanged)"""
    print("Section detector module loaded successfully")

    # init_db(Base)
    # Register centralized error handlers for meaningful errors (NFR-004)
    try:
        register_error_handlers(app)
    except Exception:
        print("Warning: failed to register error handlers")


try:
    register_error_handlers(app)
except Exception:
    print("Warning: failed to register error handlers at import time")

ENFORCE_HTTPS = os.getenv("ENFORCE_HTTPS", "false").lower() == "true"


@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    """Enforce HTTPS (unchanged)"""
    if ENFORCE_HTTPS:
        proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        if proto != "https":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(url), status_code=307)
    response = await call_next(request)
    return response
