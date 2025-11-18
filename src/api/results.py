"""
Results API - Returns parsed resume with validation and feedback

[FIX] This file is now refactored to use the central
`get_analysis_data` function from data_service.py.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

# Import the new service function
from src.api.data_service import get_analysis_data, UPLOAD_DIR, extract_text_from_file

router = APIRouter()


@router.get("/results/{job_id}")
async def get_results(job_id: str) -> Dict[str, Any]:
    """
    Get resume analysis results with validation and feedback.
    """
    try:
        # Just call the one, central function
        report_data = get_analysis_data(job_id)
        return report_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_results endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing results: {str(e)}",
        )


@router.get("/results/{job_id}/raw")
async def get_raw_text(job_id: str) -> Dict:
    """
    Get raw extracted text from resume (for debugging)
    """
    if not job_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job ID not found"
        )
    uploaded_files = list(UPLOAD_DIR.glob(f"{job_id}.*"))
    if not uploaded_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No file found for job ID: {job_id}",
        )
    file_path = uploaded_files[0]
    try:
        raw_text = extract_text_from_file(file_path)
        return {
            "jobId": job_id,
            "filename": file_path.name,
            "raw_text": raw_text,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting text: {str(e)}",
        )
