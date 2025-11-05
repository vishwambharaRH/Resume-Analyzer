"""
Results API - Returns parsed resume with validation and feedback
Implements: GET /api/v1/results/{jobId}
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, status
from src.parser.section_detector import SectionDetector
from src.feedback.feedback_generator import FeedbackGenerator

router = APIRouter()
detector = SectionDetector()
feedback_gen = FeedbackGenerator()


@router.get("/results/{job_id}")
async def get_results(job_id: str) -> Dict:
    """
    Get resume analysis results with validation and feedback

    Args:
        job_id: Unique job identifier

    Returns:
        Complete analysis including:
        - Section validation
        - Incomplete section feedback
        - Missing section alerts
        - Actionable suggestions

    Requirements: FR-003, FR-010, NFR-005
    """
    if not job_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job ID not found"
        )

    # Mock resume with incomplete sections (demonstrates FR-003)
    mock_sections = {
        "education": "BS Computer Science MIT",  # Incomplete - only 4 words
        "skills": "Python JavaScript React FastAPI Docker AWS Git",  # Complete
        "experience": "Software Engineer Google",  # Incomplete - no details
        "projects": "",  # Empty - very incomplete
    }

    mock_resume_text = "\n".join(
        [f"{section.upper()}\n{content}" for section, content in mock_sections.items()]
    )

    # Run validation
    validation = detector.validate_resume_structure(mock_resume_text)

    # Generate comprehensive feedback (FR-003)
    feedback = feedback_gen.generate_comprehensive_feedback(mock_sections, validation)

    return {
        "status": "completed",
        "jobId": job_id,
        "sections": mock_sections,
        "validation": validation,
        "feedback": feedback,
    }
