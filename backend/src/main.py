from fastapi import FastAPI
from src.upload.routes import router as upload_router

app = FastAPI(title="Resume Analyzer API")

# Register upload routes
app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])

@app.get("/")
def root():
    return {"message": "Resume Analyzer API is running"}
