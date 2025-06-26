#!/usr/bin/env python3
"""
Test script for real AI pipeline.
Make sure to set OPENAI_API_KEY environment variable before running.
"""

import os
import asyncio
import json
from app.comic_pipeline import create_comic_pipeline

async def test_real_ai_pipeline():
    """Test the real AI pipeline with OpenAI"""
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("✅ OpenAI API key found")
    
    # Create pipeline
    pipeline = create_comic_pipeline()
    
    # Test state
    test_state = {
        "prompt": "A robot and a cat having a tea party in a garden",
        "style": "Pixar",
        "panels": 3
    }
    
    print(f"🎨 Testing pipeline with: {test_state['prompt']}")
    print(f"📊 Style: {test_state['style']}, Panels: {test_state['panels']}")
    print("⏳ Running pipeline...")
    
    try:
        result = await pipeline(test_state)
        
        print("✅ Pipeline completed successfully!")
        print(f"📝 Job ID: {result.get('job_id')}")
        print(f"💬 Message: {result.get('message')}")
        
        # Check results
        if "scene" in result:
            scene = result["scene"]
            print(f"🎭 Scene parsed: {len(scene.get('characters', []))} characters in {scene.get('setting', 'unknown')}")
        
        if "panel_descriptions" in result:
            panels = result["panel_descriptions"]
            print(f"📋 Generated {len(panels)} panel descriptions")
            for i, panel in enumerate(panels[:2]):  # Show first 2
                print(f"   Panel {i+1}: {panel[:100]}...")
        
        if "image_data" in result:
            images = result["image_data"]
            print(f"🖼️  Generated {len(images)} images")
        
        if "comic_data" in result:
            comic_data = result["comic_data"]
            print(f"🎨 Final comic assembled ({len(comic_data)} base64 characters)")
        
        if "messages" in result:
            print("📨 Pipeline messages:")
            for msg in result["messages"]:
                print(f"   - {msg}")
        
        print("\n🎉 Real AI pipeline test successful!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_ai_pipeline()) 