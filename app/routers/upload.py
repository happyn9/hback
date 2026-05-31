from fastapi import APIRouter, UploadFile, File
import shutil
import os
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"http://localhost:8000/uploads/{filename}"
    }