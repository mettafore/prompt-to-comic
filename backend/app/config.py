from pydantic_settings import BaseSettings
from typing import Optional
import os

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
    port: int = 8000
    debug: bool = False
    
    # Job Configuration
    max_panels: int = 6
    min_panels: int = 2
    
    # Image Generation Settings
    image_width: int = 800
    image_height: int = 600
    image_quality: str = "standard"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure output directories exist
os.makedirs(settings.storage_dir, exist_ok=True)
os.makedirs(settings.comic_output_dir, exist_ok=True) 