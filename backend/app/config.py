from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Image Generation API
    image_api_url: Optional[str] = None
    image_api_key: Optional[str] = None
    
    # Storage Configuration
    storage_dir: str = "./output"
    comic_output_dir: str = "./output/comics"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001  # Updated to match our setup
    debug: bool = False
    
    # Job Configuration
    max_panels: int = Field(default=6, env="MAX_PANELS")
    min_panels: int = Field(default=2, env="MIN_PANELS")
    
    # Image Generation Settings
    image_width: int = Field(default=1024, env="IMAGE_WIDTH")
    image_height: int = Field(default=1024, env="IMAGE_HEIGHT")
    image_quality: str = Field(default="standard", env="IMAGE_QUALITY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure output directories exist
os.makedirs(settings.storage_dir, exist_ok=True)
os.makedirs(settings.comic_output_dir, exist_ok=True)

# Validate OpenAI API key
if not settings.openai_api_key:
    # Try to get from environment variable
    settings.openai_api_key = os.getenv("OPENAI_API_KEY") 