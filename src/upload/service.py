"""
File upload service
Implements DRA-41: File storage and management
"""

import os
import uuid
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from typing import List
from src.utils.timeit import timeit
from src.parser.analyzer import run_analysis

# ✅ Required global constant — tests rely on this
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def analyze_resume_with_gaps(job_id: str, file_path: str):
    """
    Background task to analyze resume for FR-009

    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded resume file
    """
    try:
        print(f"🔍 Starting FR-009 analysis for job {job_id}")

        from src.parser.text_extractor import TextExtractor
        from src.parser.experience_parser import ExperienceParser
        from src.parser.gap_detector import GapDetector
        from src.parser.analyzer import analysis_results

        # Extract text
        extractor = TextExtractor()
        resume_text = extractor.extract_text(file_path)

        if not resume_text:
            print(f"❌ Could not extract text for job {job_id}")
            return

        # Parse experience
        exp_parser = ExperienceParser()
        experience_data = exp_parser.parse_experience_section(resume_text)

        print(f"📄 Found {len(experience_data)} jobs for {job_id}")

        # Detect gaps
        gap_detector = GapDetector()
        analysis = gap_detector.analyze_resume(resume_text, experience_data)

        # Store results
        if job_id not in analysis_results:
            analysis_results[job_id] = {}

        analysis_results[job_id].update(
            {
                "word_count": analysis["word_count"],
                "word_count_status": analysis["word_count_status"],
                "word_count_feedback": analysis["word_count_feedback"],
                "employment_gaps": analysis["employment_gaps"],
                "gap_count": analysis["gap_count"],
                "gap_feedback": analysis["gap_feedback"],
            }
        )

        print(
            f"✅ FR-009 complete: {analysis['word_count']} words, {analysis['gap_count']} gaps"
        )

    except Exception as e:
        print(f"❌ FR-009 failed for {job_id}: {e}")
        import traceback

        traceback.print_exc()


# ✅ Alias for backward compatibility
analyze_resume_background = analyze_resume_with_gaps


@timeit("save_file")
async def save_file(file: UploadFile) -> dict:
    """
    Save uploaded file and trigger background analysis.
    Ensures directory exists (required by tests).
    """
    # ✅ Ensure upload directory exists (exact behavior tests expect)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    job_id = str(uuid.uuid4())
    file_ext = Path(getattr(file, "filename", "")).suffix
    unique_filename = f"{job_id}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Read file contents
    content = await file.read()

    # ✅ Save file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # ✅ Schedule both Sprint 1 and Sprint 2 analysis
    try:
        asyncio.create_task(run_analysis(str(file_path), job_id))
        asyncio.create_task(analyze_resume_with_gaps(job_id, str(file_path)))
    except RuntimeError:
        # ✅ For AnyIO / trio tests fallback
        import anyio

        async with anyio.create_task_group() as tg:
            tg.start_soon(run_analysis, str(file_path), job_id)
            tg.start_soon(analyze_resume_with_gaps, job_id, str(file_path))

    return {
        "job_id": job_id,
        "original_filename": getattr(file, "filename", None),
        "stored_filename": unique_filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "upload_time": datetime.utcnow().isoformat(),
        "status": "uploaded",
    }


def delete_file(file_path: str) -> bool:
    """Delete file from disk."""
    path = Path(file_path)
    try:
        if path.exists():
            path.unlink()
            return True
        return False
    except OSError:
        return False


def schedule_file_cleanup(file_path: str, delay_seconds: int = 30) -> None:
    """Schedule file deletion after delay."""

    def _del():
        try:
            delete_file(file_path)
        except Exception:
            import logging

            logging.getLogger(__name__).exception("File cleanup failed: %s", file_path)

    t = threading.Timer(delay_seconds, _del)
    t.daemon = True
    t.start()


async def process_batch_upload(files: List[UploadFile]) -> List[dict]:
    """
    Processes a batch of uploaded resume files.
    (Implements DRA-101)
    """
    job_results = []

    for file in files:
        # 1. Save the file first
        file_meta = await save_file(file)

        # 2. Get the job_id and file_path from the metadata
        job_id = file_meta.get("job_id")
        file_path = file_meta.get("file_path")

        if not job_id or not file_path:
            job_results.append(
                {
                    "jobId": None,
                    "filename": file.filename,
                    "status": "failed",
                    "error": "Failed to save file",
                }
            )
            continue

        # 3. Append the job info to our results
        job_results.append(
            {
                "jobId": job_id,
                "filename": file.filename,
                "status": "processing",
            }
        )

    return job_results

import logging
logger = logging.getLogger(__name__)

def delete_and_log(file_path: str) -> bool:
    """
    Delete a file and log the action.
    Required by integration tests.
    """
    try:
        deleted = delete_file(file_path)
        if deleted:
            logger.info(f"Deleted file: {file_path}")
        else:
            logger.warning(f"File not found for deletion: {file_path}")
        return deleted
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        raise
