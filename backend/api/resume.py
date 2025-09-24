from fastapi import APIRouter, UploadFile, File
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from utils import filecleaner
from sentence_transformers import SentenceTransformer
from transformers import pipeline

import tempfile

model = SentenceTransformer("all-MiniLM-L6-v2")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
ner_pipe = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple") # for summary
generator = pipeline("text2text-generation", model="google/flan-t5-large")  # for strengths/weaknesses

router = APIRouter()

@router.post("/analyze")
async def upload_resume(file: UploadFile = File(...)):

    if not file.filename.endswith('.pdf'):
        return {"error": "Only PDF files are accepted."}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    
    normalized_file = filecleaner.extract_and_clean(tmp_path)

    summary = summarizer(normalized_file, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

    strengths_text = generator(
        f"""From this resume, list 3 main strengths focusing ONLY on technical skills, tools, and projects. 
    Ignore the person's name, email, location, or contact details.

    Resume:
    {normalized_file}""",
        max_length=128
    )[0]["generated_text"]

    weaknesses_text = generator(
        f"""From this resume, identify 3 weaknesses or areas of improvement, 
    such as missing details, unclear experience, or lack of measurable achievements. 
    Ignore personal information like name, email, or address.

    Resume:
    {normalized_file}""",
        max_length=128
    )[0]["generated_text"]

    entities = ner_pipe(normalized_file[:1000])

    suggestions = []
    if "experience" not in normalized_file.lower():
        suggestions.append("Add a dedicated Experience section with clear job roles.")
    if "education" not in normalized_file.lower():
        suggestions.append("Include your academic background and achievements.")
    suggestions.append("Include measurable results (e.g., 'improved efficiency by 20%').")

    return {
        "filename": file.filename,
        "summary": summary,
        "strengths": strengths_text,
        "weaknesses": weaknesses_text,
        "suggestions": suggestions,
        "entities_sample": [
            {**ent, "score": float(ent["score"])} for ent in entities[:5]
        ],
        "preview_text": normalized_file[:300]
    }