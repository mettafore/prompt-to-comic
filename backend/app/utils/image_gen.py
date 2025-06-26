"""
Image generation utilities for the comic pipeline.
"""

import logging
import base64
from io import BytesIO
from typing import Optional
from openai import AsyncOpenAI
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Image generator using DALL-E"""
    
    def __init__(self, api_key: str, model: str = "dall-e-3"):
        logger.debug(f"🎨 ImageGenerator: Initializing with model={model}")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.debug(f"✅ ImageGenerator: Initialized successfully")
    
    async def generate_image(self, prompt: str, size: str = "1024x1024") -> bytes:
        """Generate image using DALL-E"""
        logger.debug(f"🎨 ImageGenerator.generate_image: Sending prompt (length={len(prompt)})")
        logger.debug(f"🎨 ImageGenerator.generate_image: Prompt preview: {prompt[:100]}...")
        logger.debug(f"🎨 ImageGenerator.generate_image: Size: {size}")
        
        try:
            response = await self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.debug(f"✅ ImageGenerator.generate_image: DALL-E response received, URL: {image_url[:50]}...")
            
            # Download the image
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        logger.debug(f"✅ ImageGenerator.generate_image: Image downloaded successfully, size: {len(image_data)} bytes")
                        return image_data
                    else:
                        logger.error(f"❌ ImageGenerator.generate_image: Failed to download image, status: {resp.status}")
                        raise Exception(f"Failed to download image: {resp.status}")
                        
        except Exception as e:
            logger.error(f"❌ ImageGenerator.generate_image: DALL-E API error: {e}")
            raise Exception(f"Failed to generate image: {e}")
    
    def create_comic_layout(self, images: list, title: str = "Comic Strip") -> bytes:
        """Create a comic layout from multiple images"""
        logger.debug(f"🎨 ImageGenerator.create_comic_layout: Creating layout with {len(images)} images, title: {title}")
        
        try:
            # Calculate layout dimensions
            num_panels = len(images)
            if num_panels == 0:
                logger.error("❌ ImageGenerator.create_comic_layout: No images provided")
                raise Exception("No images provided")
            
            # Create a simple grid layout
            cols = min(3, num_panels)
            rows = (num_panels + cols - 1) // cols
            
            logger.debug(f"📐 ImageGenerator.create_comic_layout: Layout grid: {rows}x{cols}")
            
            # Standard panel size
            panel_width = 300
            panel_height = 300
            margin = 20
            
            # Calculate total dimensions
            total_width = cols * panel_width + (cols + 1) * margin
            total_height = rows * panel_height + (rows + 1) * margin + 100  # Extra space for title
            
            logger.debug(f"📐 ImageGenerator.create_comic_layout: Canvas size: {total_width}x{total_height}")
            
            # Create canvas
            canvas = Image.new('RGB', (total_width, total_height), 'white')
            draw = ImageDraw.Draw(canvas)
            
            # Add title
            try:
                font = ImageFont.truetype("Arial.ttf", 24)
                logger.debug("✅ ImageGenerator.create_comic_layout: Using Arial font")
            except:
                font = ImageFont.load_default()
                logger.debug("🔄 ImageGenerator.create_comic_layout: Using default font")
            
            draw.text((margin, margin), title, fill='black', font=font)
            logger.debug(f"📝 ImageGenerator.create_comic_layout: Added title: {title}")
            
            # Place images
            for i, image_data in enumerate(images):
                row = i // cols
                col = i % cols
                
                x = margin + col * (panel_width + margin)
                y = margin + 100 + row * (panel_height + margin)  # Start below title
                
                logger.debug(f"🖼️ ImageGenerator.create_comic_layout: Processing panel {i+1} at position ({x}, {y})")
                
                # Convert bytes to PIL Image
                image = Image.open(BytesIO(image_data))
                image = image.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
                
                # Paste onto canvas
                canvas.paste(image, (x, y))
                
                # Add panel number
                draw.text((x + 5, y + 5), f"Panel {i+1}", fill='white', font=font)
                
                logger.debug(f"✅ ImageGenerator.create_comic_layout: Panel {i+1} placed successfully")
            
            # Convert back to bytes
            output = BytesIO()
            canvas.save(output, format='PNG')
            final_data = output.getvalue()
            
            logger.debug(f"✅ ImageGenerator.create_comic_layout: Layout created successfully, size: {len(final_data)} bytes")
            return final_data
            
        except Exception as e:
            logger.error(f"❌ ImageGenerator.create_comic_layout: Layout creation error: {e}")
            raise Exception(f"Failed to create comic layout: {e}")

# Global image generator instance
image_generator = None

def get_image_generator(api_key: str = None) -> ImageGenerator:
    """Get or create image generator instance"""
    global image_generator
    logger.debug(f"🔍 get_image_generator: Requested image generator")
    
    if image_generator is None:
        if api_key is None:
            logger.error("❌ get_image_generator: No API key provided")
            raise Exception("OpenAI API key required")
        
        logger.debug("🔧 get_image_generator: Creating new image generator instance")
        image_generator = ImageGenerator(api_key=api_key)
        logger.debug("✅ get_image_generator: Image generator created successfully")
    else:
        logger.debug("✅ get_image_generator: Returning existing image generator instance")
    
    return image_generator 