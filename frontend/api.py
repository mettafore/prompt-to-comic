# Dummy API functions for frontend scaffolding

def generate_comic(prompt: str, style: str, panels: int):
    # Simulate backend response
    return {"job_id": "dummy123"}

def check_job_status(job_id: str):
    # Simulate polling and completion
    # Always return done with a placeholder image
    return {
        "state": "done",
        "comic_url": "https://placehold.co/800x300/png?text=Your+Comic+Here",
        "pdf_url": "https://placehold.co/800x300/pdf?text=Your+Comic+PDF"
    } 