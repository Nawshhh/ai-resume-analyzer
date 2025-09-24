from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from utils import filecleaner

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    if not file.filename.endswith('.pdf'):
        return {"error": "Only PDF files are accepted."}

    # text = extract_text(file.file)

    normalized_file = filecleaner.extract_and_clean(file.file)

    return {"filename" : file.filename, "content_type" : file.content_type, "text" : normalized_file}  