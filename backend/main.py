from typing import Union
from fastapi import FastAPI
from api import resume

app = FastAPI(title="AI Resume Analyzer", version="1.0")

app.include_router(resume.router, prefix="/resume", tags=["resume"])

@app.get("/")
async def read_root():
    return {"Hello": "World"}
