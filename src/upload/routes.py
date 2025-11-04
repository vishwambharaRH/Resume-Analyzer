"""
Resume upload API routes
Implements DRA-41: Upload endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.upload.validators import (
    validate_file_type,
    validate_file_size,
    validate_file_content,
)
from src.upload.service import save_file

router = APIRouter()


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload resume file for analysis

    Accepts:
        .pdf, .docx, .txt
    Max size:
        10MB

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

    # Read file content for validation
    content = await file.read()
    await file.seek(0)  # Reset file pointer for later reading

    # Validate file size
    is_valid, error_msg = validate_file_size(len(content))
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=error_msg,
        )

    # Validate file content (magic bytes & UTF-8 for txt)
    is_valid, error_msg = validate_file_content(content[:2048], file.filename)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=error_msg,
        )

    # Save file
    try:
        result = await save_file(file)
        return {
            "jobId": result["job_id"],
            "status": "processing",
            "message": "Resume received for analysis.",
            "originalFilename": result["original_filename"],
            "fileSize": result["file_size"],
        }

    except Exception as exc:  # noqa: W0718
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(exc)}",
        ) from exc


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "upload"}
