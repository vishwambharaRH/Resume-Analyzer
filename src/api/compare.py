"""
Job Description Comparison API Endpoint (FastAPI)
Handles resume vs JD matching requests.

[DRA-62 FIX] This file is now updated to call BOTH the JDMatcher and the
FeedbackGenerator to create a final, combined 'overall_score'.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
import logging
import tempfile
import os
import uuid

from src.parser.jd_parser import JDParser
from src.parser.jd_matcher import JDMatcher
from src.parser.analyzer import run_analysis
from pathlib import Path

# [DRA-62 FIX] Step 1: Import the FeedbackGenerator
from src.feedback.feedback_generator import FeedbackGenerator

logger = logging.getLogger(__name__)

# Router mounted at /api/v1/compare in main.py
router = APIRouter(prefix="/api/v1/compare", tags=["compare"])

# Initialize parsers / matchers
jd_parser = JDParser()
matcher = JDMatcher()

# [DRA-62 FIX] Step 2: Initialize the FeedbackGenerator
feedback_gen = FeedbackGenerator()


def convert_analyzer_results_to_standard_format(analysis_result: dict) -> dict:
    """
    Convert analyzer output to the resume_data format that JDMatcher expects.
    (This function remains unchanged)
    """
    if (
        not isinstance(analysis_result, dict)
        or analysis_result.get("status") != "complete"
    ):
        raise ValueError("Analyzer did not return a complete analysis result")

    analysis = analysis_result.get("analysis", {})

    # Extract skills
    skills = []
    skills_obj = analysis.get("skills", {})
    if isinstance(skills_obj, dict):
        # collect any lists inside skills (technical_skills, etc.)
        for v in skills_obj.values():
            if isinstance(v, list):
                skills.extend(v)
    elif isinstance(skills_obj, list):
        skills.extend(skills_obj)

    # Extract merged sections if available
    structure = analysis.get("structure", {})
    merged = structure.get("merged_sections", {}) if isinstance(structure, dict) else {}

    experience_text = merged.get("experience", "") or ""
    education_text = merged.get("education", "") or ""
    skills_from_merged = merged.get("skills", "")
    if isinstance(skills_from_merged, str) and skills_from_merged:
        # try splitting a comma-separated skills string
        for s in [s.strip() for s in skills_from_merged.split(",") if s.strip()]:
            if s and s not in skills:
                skills.append(s)

    # Normalize skill strings
    skills = [s for s in skills]

    return {
        "skills": skills,
        "experience": experience_text,
        "education": education_text,
    }


@router.post("/", status_code=status.HTTP_200_OK)
async def compare_resume_with_jd(
    file: Optional[UploadFile] = File(None, description="Resume file (PDF, DOCX, TXT)"),
    job_description: Optional[str] = Form(None, description="Job description text"),
):
    """
    Compare resume against job description.
    Accepts multipart/form-data with file + job_description.
    """
    # Basic validation (unchanged)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Resume file is required"
        )

    # Missing JD entirely → 400 (unit test expects this)
    if job_description is None:
        raise HTTPException(status_code=400, detail="job_description is required")

    # Provided but empty string → 422 (integration test expects 200 or 422 allowed)
    if isinstance(job_description, str) and job_description.strip() == "":
        raise HTTPException(status_code=422, detail="job_description cannot be empty")


    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected"
        )

    allowed_extensions = {"pdf", "docx", "txt"}
    file_ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    # Save file temporarily (unchanged)
    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_file_path = tmp.name

        # Run analysis (async) (unchanged)
        job_id = str(uuid.uuid4())
        logger.info(f"Running analyzer for job {job_id}")
        analysis_result = await run_analysis(tmp_file_path, job_id)

        # Convert analyzer result to the format JDMatcher expects (unchanged)
        resume_data = convert_analyzer_results_to_standard_format(analysis_result)

        # Parse JD (unchanged)
        logger.info("Parsing job description")
        jd_req = jd_parser.parse_job_description(job_description)

        # Match resume -> JD using JDMatcher (unchanged)
        logger.info("Matching resume against JD")
        match_result = matcher.match_resume_to_jd(resume_data, job_description)

        # -----------------------------------------------------------------
        # [DRA-62 FIX] Step 3: Call your NEW scoring logic
        # -----------------------------------------------------------------
        logger.info("Running new DRA-62 comprehensive feedback generation")

        # We need to build the 'validation' and 'sections' dicts that
        # your new function expects.

        analysis_data = analysis_result.get("analysis", {})
        structure_data = analysis_data.get("structure", {})

        # 1. Get the sections text (e.g., {"experience": "...", "education": "..."})
        sections_data = structure_data.get("merged_sections", {})

        # 2. Build the validation dictionary
        validation_data = {
            "completeness_score": structure_data.get("completeness_score", 0),
            "has_all_required": structure_data.get("has_all_required", False),
            "missing_sections": structure_data.get("missing_sections", []),
            "present_sections": structure_data.get("present_sections", []),
            # This is the critical link:
            # Pass the Job Fit score (the 60%) into the new function
            "keyword_match_score": match_result.get("fit_percentage", 0),
        }

        # 3. Call the Feedback Generator to get the final combined score
        # This function runs all logic: grammar, verbs, and your new _calculate_final_score
        final_report_data = feedback_gen.generate_comprehensive_feedback_with_grammar(
            sections=sections_data, validation=validation_data, include_grammar=True
        )

        # -----------------------------------------------------------------
        # [DRA-62 FIX] Step 4: Build the final response
        # -----------------------------------------------------------------

        # Get the new final score (the 57!)
        final_overall_score = final_report_data.get("overall_score", 0)

        # Build the final response, using the 'match_result' as the base
        # (since the frontend is already built for it) and ADDING our new score.
        response = {
            # --- This is the OLD score (the 60%) ---
            "fit_percentage": match_result.get("fit_percentage", 0.0),
            # --- This is the NEW score (the 57!) ---
            "overall_score": final_overall_score,
            # --- All the other data the frontend needs ---
            "fit_category": match_result.get("fit_category", ""),
            "matched_skills": match_result.get("matched_skills", []),
            "missing_skills": match_result.get("missing_skills", []),
            "recommendations": match_result.get("recommendations", []),
            "skill_match_percentage": match_result.get("skill_match_percentage", 0.0),
            "experience_match_percentage": match_result.get(
                "experience_match_percentage", 0.0
            ),
            "education_match_percentage": match_result.get(
                "education_match_percentage", 0.0
            ),
            "explanation": match_result.get("explanation", ""),
            "match_details": match_result.get("match_details", {}),
            # [DRA-62 FIX] Also pass through the new feedback data
            "grammar_feedback": final_report_data.get("grammar", {}),
            "action_verb_feedback": final_report_data.get("action_verbs", {}),
            "overall_suggestions": final_report_data.get("suggestions", []),
        }

        logger.info(f"Job Fit Score (DRA-18): {response['fit_percentage']}")
        logger.info(f"Final Overall Score (DRA-62): {response['overall_score']}")

        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error("Error in compare endpoint: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error in compare endpoint: {str(e)}",
        )

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception:
                pass


@router.get("/health")
async def health_check():
    """Health check for compare service."""
    return {"status": "healthy", "service": "compare"}
