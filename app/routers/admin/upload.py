import os
import shutil
from fastapi import APIRouter, UploadFile, File
from datetime import datetime

router = APIRouter()
UPLOAD_DIR = "app/static/image"

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = int(datetime.utcnow().timestamp())
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": filename}  # Trả về filename, frontend sẽ dùng serialize() để tạo URL đầy đủ