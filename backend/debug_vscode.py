#!/usr/bin/env python3
"""
VSCode Debug Script for Comic Pipeline
Run this with VSCode debugger to test the pipeline step by step.
"""

import argparse
import asyncio
import logging
import os
import sys
import base64
from pathlib import Path
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.comic_pipeline import create_comic_pipeline

def setup_logging():
    """Set up logging for debugging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def save_images_to_disk(result, output_dir: str):
    """Save generated images and comic to disk"""
    logger = logging.getLogger(__name__)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save individual panel images
    if "image_data" in result:
        panel_images = result["image_data"]
        logger.info(f"💾 Saving {len(panel_images)} panel images to {output_path}")
        
        for i, img_b64 in enumerate(panel_images):
            try:
                img_data = base64.b64decode(img_b64)
                panel_filename = output_path / f"panel_{i+1}_{timestamp}.png"
                
                with open(panel_filename, 'wb') as f:
                    f.write(img_data)
                
                logger.info(f"✅ Saved panel {i+1}: {panel_filename}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save panel {i+1}: {e}")
    
    # Save final comic
    if "comic_data" in result:
        try:
            comic_data = base64.b64decode(result["comic_data"])
            comic_filename = output_path / f"comic_{timestamp}.png"
            
            with open(comic_filename, 'wb') as f:
                f.write(comic_data)
            
            logger.info(f"✅ Saved comic: {comic_filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save comic: {e}")
    
    # Save metadata
    try:
        metadata = {
            "prompt": result.get("prompt", ""),
            "style": result.get("style", ""),
            "panels": result.get("panels", 0),
            "job_id": result.get("job_id", ""),
            "scene": result.get("scene", {}),
            "panel_descriptions": result.get("panel_descriptions", []),
            "messages": result.get("messages", []),
            "timestamp": timestamp
        }
        
        metadata_filename = output_path / f"metadata_{timestamp}.json"
        import json
        with open(metadata_filename, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Saved metadata: {metadata_filename}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save metadata: {e}")
    
    return output_path

async def debug_pipeline(prompt: str, style: str, panels: int, save_output: bool = True):
    """Debug the comic pipeline with given parameters"""
    logger = logging.getLogger(__name__)
    
    logger.info("🐛 Starting VSCode Debug Session")
    logger.info("=" * 60)
    logger.info(f"📝 Prompt: {prompt}")
    logger.info(f"🎨 Style: {style}")
    logger.info(f"📊 Panels: {panels}")
    logger.info("=" * 60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not set!")
        logger.error("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    logger.info("✅ API key found")
    
    # Create pipeline
    logger.info("🔧 Creating pipeline...")
    pipeline = create_comic_pipeline()
    logger.info("✅ Pipeline created")
    
    # Prepare state
    pipeline_state = {
        "prompt": prompt,
        "style": style,
        "panels": panels
    }
    
    logger.info(f"📋 Pipeline state prepared: {pipeline_state}")
    
    # Set breakpoint here to start debugging
    logger.info("🚀 Starting pipeline execution...")
    logger.info("💡 Set breakpoints in comic_pipeline.py functions to debug step by step")
    
    try:
        # This is where you can set breakpoints in VSCode
        result = await pipeline(pipeline_state)
        
        logger.info("✅ Pipeline completed!")
        logger.info(f"📊 Result keys: {list(result.keys())}")
        
        if "error" in result:
            logger.error(f"❌ Pipeline error: {result['error']}")
        else:
            logger.info(f"✅ Success! Message: {result.get('message', 'No message')}")
            logger.info(f"📝 Panel descriptions: {len(result.get('panel_descriptions', []))}")
            logger.info(f"🖼️  Images generated: {len(result.get('image_data', []))}")
            
            # Show panel descriptions
            for i, desc in enumerate(result.get('panel_descriptions', [])):
                logger.info(f"   Panel {i+1}: {desc}")
            
            # Show scene data
            scene = result.get('scene', {})
            logger.info(f"🎭 Scene data: {scene}")
            
            # Save to disk if requested
            if save_output:
                output_dir = f"output/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                saved_path = save_images_to_disk(result, output_dir)
                logger.info(f"💾 All files saved to: {saved_path}")
            
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function with argparse"""
    parser = argparse.ArgumentParser(description="Debug Comic Pipeline with VSCode")
    parser.add_argument(
        "--prompt", 
        type=str, 
        default="A robot and a cat having a tea party in a garden",
        help="Comic prompt description"
    )
    parser.add_argument(
        "--style", 
        type=str, 
        default="Manga",
        choices=["Manga", "Graphic Novel", "Pixar", "Noir"],
        help="Art style for the comic"
    )
    parser.add_argument(
        "--panels", 
        type=int, 
        default=3,
        choices=range(2, 7),
        help="Number of panels (2-6)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--no-save", 
        action="store_true",
        help="Don't save images to disk (keep in memory only)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        setup_logging()
    else:
        logging.basicConfig(level=logging.INFO)
    
    print("🐛 VSCode Debug Script for Comic Pipeline")
    print("=" * 60)
    print(f"📝 Prompt: {args.prompt}")
    print(f"🎨 Style: {args.style}")
    print(f"📊 Panels: {args.panels}")
    print(f"💾 Save to disk: {not args.no_save}")
    print("=" * 60)
    print("💡 Set breakpoints in comic_pipeline.py to debug step by step")
    print("💡 Use F5 in VSCode to start debugging")
    print("=" * 60)
    
    # Run the debug function
    asyncio.run(debug_pipeline(args.prompt, args.style, args.panels, save_output=not args.no_save))

if __name__ == "__main__":
    main() 