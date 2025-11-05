"""
Results API - Returns parsed resume with validation
Implements: GET /api/v1/results/{jobId}
"""

from typing import Dict
from fastapi import APIRouter, HTTPException, status
from src.parser.section_detector import SectionDetector

router = APIRouter()
detector = SectionDetector()


@router.get("/results/{job_id}")
async def get_results(job_id: str) -> Dict:
    """
    Get resume analysis results including missing sections

    Returns validation feedback with:
    - Missing sections
    - Completeness score
    - Present sections
    """
    if not job_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job ID not found"
        )

    # TODO: Retrieve actual parsed data from database
    # For now, return mock data with section validation

    # Mock resume text (replace with actual database query)
    mock_resume_text = """
    JOHN DOE
    john@example.com

    EDUCATION
    BS Computer Science, MIT, 2020

    EXPERIENCE
    Software Engineer, Google, 2020-Present
    Developed scalable APIs

    PROJECTS
    AI Chatbot using NLP
    Built with Python and spaCy
    """

    # Run validation
    validation = detector.validate_resume_structure(mock_resume_text)

    return {
        "status": "completed",
        "jobId": job_id,
        "sections": {
            "education": ["BS Computer Science, MIT, 2020"],
            "skills": [],
            "experience": ["Software Engineer, Google, 2020-Present"],
            "projects": ["AI Chatbot using NLP"],
        },
        "validation": validation,
        "feedback": {
            "strengths": (
                [
                    f"{len(validation['present_sections'])} sections present",
                    "Clear structure",
                ]
                if validation["has_all_required"]
                else ["Resume partially complete"]
            ),
            "improvements": [
                f"Add {section} section"
                for section in validation["missing_sections"]
            ],
            "score": int(validation["completeness_score"]),
        },
    }
