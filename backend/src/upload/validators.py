import os

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

def validate_file_type(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS
