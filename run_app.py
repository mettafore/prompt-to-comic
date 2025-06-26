#!/usr/bin/env python3
"""
Script to run both backend and frontend for Prompt-to-Comic app
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server"""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    
    # Start backend
    backend_process = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_dir,
        env=env
    )
    
    print("✅ Backend server started on http://localhost:8000")
    return backend_process

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Start frontend
    frontend_process = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"],
        cwd=frontend_dir
    )
    
    print("✅ Frontend started on http://localhost:8501")
    return frontend_process

def main():
    """Main function to run both services"""
    print("🎨 Prompt-to-Comic App")
    print("=" * 50)
    
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("✅ API key found")
    
    try:
        # Start backend
        backend_process = run_backend()
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend
        frontend_process = run_frontend()
        
        print("\n" + "=" * 50)
        print("🎉 Both services are running!")
        print("📱 Frontend: http://localhost:8501")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("=" * 50)
        print("Press Ctrl+C to stop both services")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        sys.exit(1)
    
    finally:
        # Clean up processes
        if 'backend_process' in locals():
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if 'frontend_process' in locals():
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 