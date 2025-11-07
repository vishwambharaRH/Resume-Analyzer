"""
File upload service
Implements DRA-41: File storage and management
"""

import uuid
import asyncio  # <-- 1. IMPORT ASYNCIO
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile

# --- 2. IMPORT YOUR NEW ANALYZER ---
from src.parser.analyzer import run_analysis

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_file(file: UploadFile) -> dict:
    """
    Save uploaded file with unique identifier.

    Args:
        file (UploadFile): Incoming file object

    Returns:
        dict: File metadata including job id, filenames, size and timestamps
    """
    job_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    unique_filename = f"{job_id}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    content = await file.read()  # async read

    # Write file to disk
    with file_path.open("wb") as file_handle:
        file_handle.write(content)

    # --- 3. ADD THIS LINE ---
    # This triggers the background job *without* making the
    # API wait. The route immediately returns the 202.
    asyncio.create_task(run_analysis(str(file_path), job_id))

    return {
        "job_id": job_id,
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "upload_time": datetime.utcnow().isoformat(),
        "status": "uploaded",
    }


def delete_file(file_path: str) -> bool:
    """
    Delete file from storage.

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except OSError:
        return False
