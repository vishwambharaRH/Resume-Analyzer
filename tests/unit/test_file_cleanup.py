import os
import time
from pathlib import Path

from src.upload.service import schedule_file_cleanup, UPLOAD_DIR


def test_schedule_file_cleanup(tmp_path):
    # create dummy file in upload dir
    UPLOAD_DIR.mkdir(exist_ok=True)
    f = UPLOAD_DIR / "temp_cleanup.txt"
    f.write_text("to be deleted")

    assert f.exists()

    schedule_file_cleanup(str(f), delay_seconds=1)

    # wait for cleanup to run
    time.sleep(2)

    assert not f.exists(), "File was not cleaned up by schedule_file_cleanup"
