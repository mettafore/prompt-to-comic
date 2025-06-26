from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# API Request/Response Models
class GenerateRequest(BaseModel):
    text: str = Field(..., description="User's creative prompt or scene description")
    style: str = Field(..., description="Art style: Graphic Novel, Manga, Pixar, Noir")
    panels: int = Field(..., ge=2, le=6, description="Number of panels (2-6)")

class GenerateResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier for tracking")

class StatusResponse(BaseModel):
    state: str = Field(..., description="Job state: pending, processing, done, failed")
    message: Optional[str] = Field(None, description="Status message or error")
    comic_url: Optional[str] = Field(None, description="URL to generated comic PNG")
    pdf_url: Optional[str] = Field(None, description="URL to generated comic PDF")

class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Health check status")

# LangGraph Pipeline Models
class SceneComponents(BaseModel):
    """Extracted components from user prompt"""
    characters: List[str] = Field(..., description="List of characters in the scene")
    setting: str = Field(..., description="Location/environment description")
    actions: List[str] = Field(..., description="Key actions happening in the scene")
    tone: str = Field(..., description="Mood/atmosphere of the scene")
    dialogue: Optional[List[str]] = Field(None, description="Any dialogue or speech")

class PanelSpec(BaseModel):
    """Specification for a single comic panel"""
    panel_number: int = Field(..., description="Panel sequence number")
    setting: str = Field(..., description="Panel-specific setting/environment")
    characters: List[str] = Field(..., description="Characters visible in this panel")
    action: str = Field(..., description="Main action happening in this panel")
    camera_angle: str = Field(..., description="Camera perspective/framing")
    mood: str = Field(..., description="Emotional tone of this panel")

class ImagePrompt(BaseModel):
    """Generated prompt for image generation"""
    panel_number: int = Field(..., description="Panel this prompt is for")
    prompt_text: str = Field(..., description="DALL·E/SDXL prompt text")
    style: str = Field(..., description="Art style being used")
    negative_prompt: Optional[str] = Field(None, description="What to avoid in the image")

class ImageFile(BaseModel):
    """Generated image file information"""
    panel_number: int = Field(..., description="Panel this image is for")
    file_path: str = Field(..., description="Local path to the image file")
    file_url: Optional[str] = Field(None, description="Public URL if available")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")

class ComicOutput(BaseModel):
    """Final comic strip output"""
    job_id: str = Field(..., description="Job identifier")
    panels: List[ImageFile] = Field(..., description="Generated panel images")
    comic_png_path: str = Field(..., description="Path to assembled comic PNG")
    comic_pdf_path: str = Field(..., description="Path to assembled comic PDF")
    comic_png_url: Optional[str] = Field(None, description="Public URL to comic PNG")
    comic_pdf_url: Optional[str] = Field(None, description="Public URL to comic PDF")

# Art Style Enum
class ArtStyle(str, Enum):
    GRAPHIC_NOVEL = "Graphic Novel"
    MANGA = "Manga"
    PIXAR = "Pixar"
    NOIR = "Noir"

# Job State Enum
class JobState(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed" 