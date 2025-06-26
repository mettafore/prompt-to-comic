# Dummy API functions for frontend scaffolding

import requests
import base64
from typing import Dict, Any

# Backend API configuration
BACKEND_URL = "http://backend:8000"

def generate_comic(prompt: str, style: str, panels: int) -> Dict[str, Any]:
    """Send comic generation request to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/generate", json={
            "text": prompt,
            "style": style,
            "panels": panels
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to backend: {str(e)}"}

def check_job_status(job_id: str) -> Dict[str, Any]:
    """Check the status of a comic generation job"""
    try:
        response = requests.get(f"{BACKEND_URL}/status/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to check status: {str(e)}"}

def get_comic_image(job_id: str) -> bytes:
    """Get the final comic image"""
    try:
        response = requests.get(f"{BACKEND_URL}/comic/{job_id}")
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        return None

def get_panel_image(job_id: str, panel_number: int) -> bytes:
    """Get a specific panel image"""
    try:
        response = requests.get(f"{BACKEND_URL}/panel/{job_id}/{panel_number}")
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        return None 