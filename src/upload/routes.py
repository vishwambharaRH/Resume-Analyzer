"""
Resume upload API routes
Implements DRA-41: Upload endpoints
"""

from typing import List
from fastapi import File, Depends
from .service import process_batch_upload  # ✅ ONLY import this
from .validators import validate_files

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
)

from src.upload.validators import (
    validate_file_type,
    validate_file_size,
    validate_file_content,
)

from src.upload.service import save_file, schedule_file_cleanup

router = APIRouter()


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload resume file for analysis

    Accepts: .pdf, .docx, .txt
    Max size: 10MB

    Returns:
        202 Accepted with job_id for tracking
    """

    # Validate file extension
    is_valid, error_msg = validate_file_type(file.filename)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=error_msg,
        )

    # Read file for validation
    content = await file.read()
    await file.seek(0)

    # Validate file size
    is_valid, error_msg = validate_file_size(len(content))
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=error_msg,
        )

    # Validate file content
    is_valid, error_msg = validate_file_content(content[:2048], file.filename)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=error_msg,
        )

    # Save file & trigger background analysis
    try:
        result = await save_file(file)
        # ✅ save_file() already triggers both Sprint 1 & Sprint 2 analysis
        # No need to call analyze_resume_background here!

        # Schedule file cleanup (NFR-002)
        schedule_file_cleanup(result["file_path"], delay_seconds=3600)

        return {
            "jobId": result["job_id"],
            "status": "processing",
            "message": "Resume received for analysis.",
            "originalFilename": result["original_filename"],
            "fileSize": result["file_size"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(exc)}",
        ) from exc


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "upload"}


@router.post(
    "/batch",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a batch of resumes",
)
async def upload_resume_batch(
    files: List[UploadFile] = File(...),
    valid_files: List[UploadFile] = Depends(validate_files),
):
    """
    Uploads and initiates analysis for a batch of resume files.
    (Implements DRA-101)
    """
    try:
        job_results = await process_batch_upload(valid_files)

        return {
            "message": f"Batch of {len(job_results)} resumes received for analysis.",
            "jobs": job_results,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during batch processing: {str(e)}",
        )
