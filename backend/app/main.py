import logging
import os
import base64
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import asyncio
from app.schemas import (
    GenerateRequest, GenerateResponse, StatusResponse, HealthResponse,
    ArtStyle, JobState
)
from app.config import settings
from app.comic_pipeline import create_comic_pipeline
import uuid

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Prompt-to-Comic API", version="0.1.0")

# Create pipeline instance
logger.debug("🚀 main: Creating comic pipeline instance")
comic_pipeline = create_comic_pipeline()
logger.debug("✅ main: Comic pipeline created")

# In-memory job storage (replace with database in production)
jobs = {}

# Create output directory
OUTPUT_DIR = Path("output/comics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_comic_files(job_id: str, result: dict):
    """Save comic files to disk"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_dir = OUTPUT_DIR / f"job_{job_id[:8]}_{timestamp}"
        job_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"💾 save_comic_files: Saving files to {job_dir}")
        
        # Save panel images
        if "image_data" in result:
            for i, img_b64 in enumerate(result["image_data"]):
                img_data = base64.b64decode(img_b64)
                panel_filename = job_dir / f"panel_{i+1}.png"
                with open(panel_filename, 'wb') as f:
                    f.write(img_data)
                logger.debug(f"✅ Saved panel {i+1}: {panel_filename}")
        
        # Save final comic
        if "comic_data" in result:
            comic_data = base64.b64decode(result["comic_data"])
            comic_filename = job_dir / "comic.png"
            with open(comic_filename, 'wb') as f:
                f.write(comic_data)
            logger.debug(f"✅ Saved comic: {comic_filename}")
        
        return str(job_dir)
        
    except Exception as e:
        logger.error(f"❌ save_comic_files: Failed to save files: {e}")
        return None

@app.post("/generate", response_model=GenerateResponse)
async def generate_comic(req: GenerateRequest):
    """Generate a comic strip from a text prompt"""
    logger.debug(f"🔍 generate_comic: Received request - style={req.style}, panels={req.panels}, text_length={len(req.text)}")
    
    # Validate art style
    if req.style not in [style.value for style in ArtStyle]:
        logger.warning(f"⚠️ generate_comic: Invalid art style '{req.style}'")
        raise HTTPException(status_code=400, detail=f"Invalid art style. Must be one of: {[style.value for style in ArtStyle]}")
    
    # Validate panel count
    if req.panels < settings.min_panels or req.panels > settings.max_panels:
        logger.warning(f"⚠️ generate_comic: Invalid panel count {req.panels}")
        raise HTTPException(status_code=400, detail=f"Panel count must be between {settings.min_panels} and {settings.max_panels}")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    logger.debug(f"🆔 generate_comic: Generated job_id: {job_id}")
    
    # Store job info
    jobs[job_id] = {
        "state": JobState.PENDING.value,
        "request": req.dict(),
        "message": "Job created successfully"
    }
    logger.debug(f"💾 generate_comic: Stored job {job_id} in memory")
    
    # Run the pipeline asynchronously
    try:
        pipeline_state = {
            "prompt": req.text,
            "style": req.style,
            "panels": req.panels,
            "job_id": job_id
        }
        
        logger.debug(f"🚀 generate_comic: Starting pipeline for job {job_id}")
        result = await comic_pipeline(pipeline_state)
        logger.debug(f"✅ generate_comic: Pipeline completed for job {job_id}")
        
        # Save files to disk
        saved_path = save_comic_files(job_id, result)
        if saved_path:
            logger.info(f"💾 generate_comic: Files saved to {saved_path}")
        
        # Update job status
        jobs[job_id] = {
            "state": JobState.DONE.value,
            "request": req.dict(),
            "result": result,
            "message": result.get("message", "Comic generated successfully"),
            "files_path": saved_path
        }
        logger.debug(f"💾 generate_comic: Updated job {job_id} status to DONE")
        
    except Exception as e:
        logger.error(f"❌ generate_comic: Pipeline failed for job {job_id}: {e}")
        jobs[job_id] = {
            "state": JobState.FAILED.value,
            "request": req.dict(),
            "message": f"Generation failed: {str(e)}"
        }
        logger.debug(f"💾 generate_comic: Updated job {job_id} status to FAILED")
    
    logger.debug(f"✅ generate_comic: Returning job_id {job_id}")
    return GenerateResponse(job_id=job_id)

@app.get("/status/{job_id}", response_model=StatusResponse)
def check_status(job_id: str):
    """Check the status of a comic generation job"""
    logger.debug(f"🔍 check_status: Checking status for job {job_id}")
    
    if job_id not in jobs:
        logger.warning(f"⚠️ check_status: Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    logger.debug(f"📊 check_status: Job {job_id} state: {job['state']}")
    
    # Get comic data from result if available
    comic_data = None
    panel_images = []
    
    if job["state"] == JobState.DONE.value and "result" in job:
        result = job["result"]
        if "comic_data" in result:
            comic_data = result["comic_data"]  # This is base64 encoded
            logger.debug(f"📄 check_status: Found comic data for job {job_id}, size: {len(comic_data)} chars")
        if "image_data" in result:
            panel_images = result["image_data"]  # This is a list of base64 encoded images
            logger.debug(f"🖼️ check_status: Found {len(panel_images)} panel images for job {job_id}")
    
    logger.debug(f"✅ check_status: Returning status for job {job_id}")
    return StatusResponse(
        state=job["state"],
        message=job.get("message", ""),
        comic_data=comic_data,
        panel_images=panel_images
    )

@app.get("/comic/{job_id}")
def get_comic(job_id: str):
    """Get the comic image directly"""
    logger.debug(f"🔍 get_comic: Getting comic for job {job_id}")
    
    if job_id not in jobs:
        logger.warning(f"⚠️ get_comic: Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["state"] != JobState.DONE.value:
        logger.warning(f"⚠️ get_comic: Job {job_id} not ready, state: {job['state']}")
        raise HTTPException(status_code=400, detail="Comic not ready yet")
    
    if "result" not in job or "comic_data" not in job["result"]:
        logger.warning(f"⚠️ get_comic: No comic data found for job {job_id}")
        raise HTTPException(status_code=404, detail="Comic data not found")
    
    # Decode base64 data
    comic_data = base64.b64decode(job["result"]["comic_data"])
    logger.debug(f"✅ get_comic: Returning comic data for job {job_id}, size: {len(comic_data)} bytes")
    
    return Response(content=comic_data, media_type="image/png")

@app.get("/panel/{job_id}/{panel_number}")
def get_panel(job_id: str, panel_number: int):
    """Get a specific panel image"""
    logger.debug(f"🔍 get_panel: Getting panel {panel_number} for job {job_id}")
    
    if job_id not in jobs:
        logger.warning(f"⚠️ get_panel: Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["state"] != JobState.DONE.value:
        logger.warning(f"⚠️ get_panel: Job {job_id} not ready, state: {job['state']}")
        raise HTTPException(status_code=400, detail="Comic not ready yet")
    
    if "result" not in job or "image_data" not in job["result"]:
        logger.warning(f"⚠️ get_panel: No panel data found for job {job_id}")
        raise HTTPException(status_code=404, detail="Panel data not found")
    
    panel_images = job["result"]["image_data"]
    
    if panel_number < 1 or panel_number > len(panel_images):
        logger.warning(f"⚠️ get_panel: Panel number {panel_number} out of range for job {job_id}")
        raise HTTPException(status_code=404, detail="Panel number out of range")
    
    # Decode base64 data
    panel_data = base64.b64decode(panel_images[panel_number - 1])
    logger.debug(f"✅ get_panel: Returning panel {panel_number} for job {job_id}, size: {len(panel_data)} bytes")
    
    return Response(content=panel_data, media_type="image/png")

@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint"""
    logger.debug("🔍 health: Health check requested")
    return HealthResponse(status="ok")

@app.get("/comics")
def list_saved_comics():
    """List all saved comics"""
    logger.debug("🔍 list_saved_comics: Listing saved comics")
    
    try:
        comics = []
        if OUTPUT_DIR.exists():
            for job_dir in OUTPUT_DIR.iterdir():
                if job_dir.is_dir():
                    comic_file = job_dir / "comic.png"
                    if comic_file.exists():
                        comics.append({
                            "job_id": job_dir.name,
                            "comic_path": str(comic_file),
                            "panels": len(list(job_dir.glob("panel_*.png"))),
                            "created": job_dir.stat().st_mtime
                        })
        
        # Sort by creation time (newest first)
        comics.sort(key=lambda x: x["created"], reverse=True)
        
        logger.debug(f"✅ list_saved_comics: Found {len(comics)} saved comics")
        return {"comics": comics}
        
    except Exception as e:
        logger.error(f"❌ list_saved_comics: Failed to list comics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list comics: {e}")

@app.get("/")
def root():
    logger.debug("🔍 root: Root endpoint requested")
    return {
        "message": "Prompt-to-Comic API",
        "version": "0.1.0",
        "docs": "/docs",
        "pipeline": "LangGraph-based comic generation with real AI",
        "saved_comics": f"/comics - List saved comics",
        "output_dir": str(OUTPUT_DIR)
    } 