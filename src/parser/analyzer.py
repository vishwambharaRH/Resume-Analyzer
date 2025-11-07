"""
Analysis Orchestrator
This module is the background worker that runs all analysis.
It is triggered by the upload service.
"""

from pathlib import Path

# --- 1. Import BOTH logic modules ---
#
# Import YOUR skill parser logic (FR-004)
from src.parser.skill_parser import get_text_from_parser, extract_skills

#
# Import the OTHER section detector logic (FR-010)
from src.parser.section_detector import SectionDetector

# (In a real app, you would import a service to save results to the DB)
# from src.api.results.service import update_job_results


async def run_analysis(file_path_str: str, job_id: str):
    """
    This is the main background task.
    It runs both parsers and saves the result.
    """
    print(f"Background Job Started: {job_id}")
    try:
        p = Path(file_path_str)

        # --- A. Parse Text ---
        # Call the text parser from your skill_parser.py
        raw_text = get_text_from_parser(p)

        if not raw_text.strip():
            raise ValueError("Could not extract text from file.")

        # --- B. Run Analyzers ---

        # 1. Your Skill Parser (FR-004)
        skill_report = extract_skills(raw_text)

        # 2. The Section Detector (FR-010)
        detector = SectionDetector()
        structure_report = detector.validate_resume_structure(raw_text)

        # --- C. Combine and Save Results ---
        final_report = {
            "status": "complete",
            "analysis": {
                "skills": skill_report,  # <-- Your code's output
                "structure": structure_report,  # <-- The other code's output
            },
        }

        # This is where you would save the final JSON to your
        # database, linking it with the job_id.
        # await update_job_results(job_id, final_report)
        print(f"Job {job_id} complete. Results: {final_report}")

    except Exception as e:
        # Save the error to the job so the frontend can see it
        error_report = {"status": "failed", "error": str(e)}
        # await update_job_results(job_id, error_report)
        print(f"Job {job_id} failed: {e}")
