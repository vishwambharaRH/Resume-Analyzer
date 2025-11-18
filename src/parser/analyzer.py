"""
Analysis Orchestrator
This module is the background worker that runs all analysis.
It is triggered by the upload service.
"""

analysis_results = {}
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
from src.parser.skill_parser import get_text_from_parser, extract_skills
from src.parser.section_detector import SectionDetector

# --- 2. NEW IMPORT FOR FR-006 ---
from src.parser.content_validator import validate_content

# Global storage for analysis results (your teammate will replace with PostgreSQL)
analysis_results = {}


async def run_analysis(file_path_str: str, job_id: str):
    """
    This is the main background task.
    Runs all analysis and stores results in analysis_results dict.
    """
    print(f"🔍 Background Job Started: {job_id}")
    try:
        p = Path(file_path_str)

        # --- A. Parse Text ---
        raw_text = get_text_from_parser(p)

        if not raw_text.strip():
            raise ValueError("Could not extract text from file.")

        # --- B. Run Analyzers ---

        # 1. Skill Parser (FR-004)
        skill_report = extract_skills(raw_text)

        # 2. Section Detector (FR-010 & FR-005)
        detector = SectionDetector()
        structure_report = detector.validate_resume_structure(raw_text)

        # 3. Content Validator (FR-006)
        validation_report = validate_content(raw_text)

        # --- C. Combine Results ---
        final_report = {
            "status": "complete",
            "analysis": {
                "skills": skill_report,
                "structure": structure_report,
                "validation": validation_report,
            },
        }

        # ✅ CRITICAL: Store results in global dict (for FR-009 to access)
        analysis_results[job_id] = final_report

        # Print completion
        print(f"✅ Job {job_id} complete")
        print(final_report)

        return final_report

    except Exception as e:
        # Save the error
        error_report = {"status": "failed", "error": str(e)}

        # ✅ CRITICAL: Store error in global dict
        analysis_results[job_id] = error_report

        print(f"❌ Job {job_id} failed: {e}")
        return error_report
