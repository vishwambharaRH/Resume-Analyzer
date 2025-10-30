from fastapi import APIRouter, UploadFile, File, HTTPException
from src.upload.validators import validate_file_type
from src.upload.service import save_file

router = APIRouter()

@router.post("/")
async def upload_resume(file: UploadFile = File(...)):
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save the file
    file_path = await save_file(file)
    return {"message": "File uploaded successfully", "path": file_path}
