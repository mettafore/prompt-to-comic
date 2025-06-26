from fastapi import FastAPI, HTTPException
from app.schemas import (
    GenerateRequest, GenerateResponse, StatusResponse, HealthResponse,
    ArtStyle, JobState
)
from app.config import settings
import uuid

app = FastAPI(title="Prompt-to-Comic API", version="0.1.0")

# In-memory job storage (replace with database in production)
jobs = {}

@app.post("/generate", response_model=GenerateResponse)
def generate_comic(req: GenerateRequest):
    """Generate a comic strip from a text prompt"""
    # Validate art style
    if req.style not in [style.value for style in ArtStyle]:
        raise HTTPException(status_code=400, detail=f"Invalid art style. Must be one of: {[style.value for style in ArtStyle]}")
    
    # Validate panel count
    if req.panels < settings.min_panels or req.panels > settings.max_panels:
        raise HTTPException(status_code=400, detail=f"Panel count must be between {settings.min_panels} and {settings.max_panels}")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Store job info (dummy for now)
    jobs[job_id] = {
        "state": JobState.PENDING.value,
        "request": req.dict(),
        "message": "Job created successfully"
    }
    
    return GenerateResponse(job_id=job_id)

@app.get("/status/{job_id}", response_model=StatusResponse)
def check_status(job_id: str):
    """Check the status of a comic generation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # For dummy backend, always return done with placeholder URLs
    return StatusResponse(
        state=JobState.DONE.value,
        message="Comic generated successfully",
        comic_url=f"/comics/{job_id}/comic.png",
        pdf_url=f"/comics/{job_id}/comic.pdf"
    )

@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint"""
    return HealthResponse(status="ok")

# Add some metadata
@app.get("/")
def root():
    return {
        "message": "Prompt-to-Comic API",
        "version": "0.1.0",
        "docs": "/docs"
    } 