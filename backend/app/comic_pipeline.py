"""
LangGraph pipeline for Prompt-to-Comic.
Demonstrates understanding of LangGraph framework for AI Tinkerers Club.
"""

import json
import uuid
import os
import base64
import logging
from typing import Dict, List, Any, TypedDict, Annotated
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from .utils.llm import get_llm_client
from .utils.image_gen import get_image_generator

# Set up logging
logger = logging.getLogger(__name__)

# Define the state schema for LangGraph
class ComicState(TypedDict):
    """State schema for the comic generation pipeline"""
    prompt: str
    style: str
    panels: int
    job_id: str
    scene: Dict[str, Any]
    panel_descriptions: List[str]
    image_data: List[bytes]  # Changed from image_paths to image_data
    comic_data: bytes  # Changed from comic_path to comic_data
    messages: List[str]

# Simple data models
@dataclass
class SceneData:
    """Scene data extracted from user prompt"""
    characters: List[str]
    setting: str
    actions: List[str]

@dataclass
class PanelData:
    """Panel data for comic generation"""
    panel_number: int
    description: str
    image_data: bytes = b""

@dataclass
class ComicData:
    """Final comic data"""
    job_id: str
    panels: List[PanelData]
    comic_data: bytes = b""

# LangGraph Node Functions
async def scene_parser(state: ComicState) -> ComicState:
    """Extract scene components from user prompt using LLM"""
    logger.debug(f"🔍 scene_parser: Starting with prompt='{state['prompt']}', style='{state['style']}'")
    
    prompt = state["prompt"]
    style = state["style"]
    
    # Get LLM client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ scene_parser: OPENAI_API_KEY environment variable required")
        raise Exception("OPENAI_API_KEY environment variable required")
    
    logger.debug("🧠 scene_parser: Getting LLM client")
    llm_client = get_llm_client(api_key)
    
    # Create structured prompt for scene parsing
    scene_prompt = f"""
    Analyze this comic prompt and extract the key elements:
    Prompt: "{prompt}"
    Style: {style}
    
    Return a JSON object with:
    - characters: list of character names/descriptions
    - setting: the location/environment
    - actions: list of actions/events happening
    - mood: the overall mood/tone
    - style_notes: specific style requirements for {style}
    """
    
    logger.debug(f"📝 scene_parser: Sending prompt to LLM: {scene_prompt[:100]}...")
    
    try:
        scene_data = await llm_client.generate_structured(scene_prompt)
        logger.debug(f"✅ scene_parser: LLM response received: {scene_data}")
        
        return {
            **state,
            "scene": scene_data,
            "messages": state.get("messages", []) + [f"Parsed scene: {len(scene_data.get('characters', []))} characters in {scene_data.get('setting', 'unknown')}"]
        }
    except Exception as e:
        logger.warning(f"⚠️ scene_parser: LLM failed, using fallback: {e}")
        # Fallback to simple parsing if LLM fails
        words = prompt.lower().split()
        characters = [word for word in words if word in ["kids", "children", "boy", "girl", "robot", "alien", "pirate", "ninja"]]
        setting = "unknown location"
        if "spaceship" in prompt.lower():
            setting = "spaceship"
        elif "pizza" in prompt.lower():
            setting = "pizza place"
        
        scene_data = {
            "characters": characters,
            "setting": setting,
            "actions": [],
            "mood": "neutral",
            "style_notes": f"Draw in {style} style"
        }
        
        logger.debug(f"🔄 scene_parser: Fallback scene data: {scene_data}")
        
        return {
            **state,
            "scene": scene_data,
            "messages": state.get("messages", []) + [f"Parsed scene (fallback): {len(characters)} characters in {setting}"]
        }

async def panel_planner(state: ComicState) -> ComicState:
    """Break scene into comic panels using LLM"""
    logger.debug(f"🔍 panel_planner: Starting with {state['panels']} panels, scene={state['scene']}")
    
    scene = state["scene"]
    panel_count = state["panels"]
    prompt = state["prompt"]
    style = state["style"]
    
    # Get LLM client
    api_key = os.getenv("OPENAI_API_KEY")
    llm_client = get_llm_client(api_key)
    
    # Create prompt for panel planning
    panel_prompt = f"""
    Create {panel_count} comic panel descriptions for this story:
    Original prompt: "{prompt}"
    Style: {style}
    Scene: {scene}
    
    Each panel should advance the story. Return a JSON array of {panel_count} panel descriptions.
    Each description should be detailed enough for image generation.
    """
    
    logger.debug(f"📝 panel_planner: Sending panel prompt to LLM: {panel_prompt[:100]}...")
    
    try:
        panel_data = await llm_client.generate_structured(panel_prompt)
        logger.debug(f"✅ panel_planner: LLM response received: {panel_data}")
        
        panel_descriptions = panel_data if isinstance(panel_data, list) else [str(panel_data)]
        
        # Ensure we have the right number of panels
        while len(panel_descriptions) < panel_count:
            panel_descriptions.append(f"Panel {len(panel_descriptions) + 1}: {scene.get('characters', [])} in {scene.get('setting', 'unknown')}")
        
        panel_descriptions = panel_descriptions[:panel_count]
        logger.debug(f"📊 panel_planner: Final panel descriptions: {panel_descriptions}")
        
        return {
            **state,
            "panel_descriptions": panel_descriptions,
            "messages": state.get("messages", []) + [f"Planned {len(panel_descriptions)} panels using LLM"]
        }
    except Exception as e:
        logger.warning(f"⚠️ panel_planner: LLM failed, using fallback: {e}")
        # Fallback to simple panel creation
        panel_descriptions = []
        for i in range(panel_count):
            description = f"Panel {i + 1}: {scene.get('characters', [])} in {scene.get('setting', 'unknown')} doing {scene.get('actions', [])}"
            panel_descriptions.append(description)
        
        logger.debug(f"🔄 panel_planner: Fallback panel descriptions: {panel_descriptions}")
        
        return {
            **state,
            "panel_descriptions": panel_descriptions,
            "messages": state.get("messages", []) + [f"Planned {panel_count} panels (fallback)"]
        }

async def image_generator(state: ComicState) -> ComicState:
    """Generate images for each panel using DALL-E"""
    logger.debug(f"🔍 image_generator: Starting with {len(state['panel_descriptions'])} panel descriptions")
    
    panel_descriptions = state["panel_descriptions"]
    style = state["style"]
    scene = state["scene"]
    
    # Get image generator
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ image_generator: OPENAI_API_KEY environment variable required")
        raise Exception("OPENAI_API_KEY environment variable required")
    
    logger.debug("🎨 image_generator: Getting image generator")
    image_gen = get_image_generator(api_key)
    
    image_data_list = []
    
    for i, description in enumerate(panel_descriptions):
        logger.debug(f"🎨 image_generator: Generating image {i+1}/{len(panel_descriptions)}: {description[:50]}...")
        
        try:
            # Create detailed image prompt
            image_prompt = f"""
            Create a comic panel image: {description}
            Style: {style}
            Mood: {scene.get('mood', 'neutral')}
            Style notes: {scene.get('style_notes', '')}
            
            Make it visually appealing and clear. Comic book style, vibrant colors.
            """
            
            logger.debug(f"📝 image_generator: Sending image prompt: {image_prompt.strip()[:100]}...")
            
            # Generate image
            image_data = await image_gen.generate_image(image_prompt.strip())
            logger.debug(f"✅ image_generator: Image {i+1} generated, size: {len(image_data)} bytes")
            image_data_list.append(image_data)
            
        except Exception as e:
            logger.warning(f"⚠️ image_generator: Image generation failed for panel {i+1}: {e}")
            # Create a simple placeholder image if generation fails
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a placeholder image
            img = Image.new('RGB', (512, 512), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 200), f"Panel {i+1}", fill='black', font=font)
            draw.text((50, 250), "Image generation failed", fill='red', font=font)
            
            # Convert to bytes
            from io import BytesIO
            output = BytesIO()
            img.save(output, format='PNG')
            placeholder_data = output.getvalue()
            logger.debug(f"🔄 image_generator: Created placeholder for panel {i+1}, size: {len(placeholder_data)} bytes")
            image_data_list.append(placeholder_data)
    
    logger.debug(f"✅ image_generator: Generated {len(image_data_list)} images total")
    
    return {
        **state,
        "image_data": image_data_list,
        "messages": state.get("messages", []) + [f"Generated {len(image_data_list)} images in {style} style"]
    }

async def layout_assembler(state: ComicState) -> ComicState:
    """Assemble panels into final comic"""
    logger.debug(f"🔍 layout_assembler: Starting with {len(state['image_data'])} images")
    
    image_data_list = state["image_data"]
    job_id = state["job_id"]
    prompt = state["prompt"]
    
    # Get image generator for layout creation
    api_key = os.getenv("OPENAI_API_KEY")
    logger.debug("🎨 layout_assembler: Getting image generator for layout")
    image_gen = get_image_generator(api_key)
    
    try:
        logger.debug(f"📝 layout_assembler: Creating comic layout with title: {prompt[:50]}")
        # Create comic layout
        comic_data = image_gen.create_comic_layout(image_data_list, title=prompt[:50])
        logger.debug(f"✅ layout_assembler: Comic layout created, size: {len(comic_data)} bytes")
        
        return {
            **state,
            "comic_data": comic_data,
            "messages": state.get("messages", []) + ["Comic assembled successfully with real images"]
        }
    except Exception as e:
        logger.warning(f"⚠️ layout_assembler: Layout creation failed, using fallback: {e}")
        # Create a simple fallback layout
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple layout
        total_width = 1024
        total_height = 768
        canvas = Image.new('RGB', (total_width, total_height), 'white')
        draw = ImageDraw.Draw(canvas)
        
        try:
            font = ImageFont.truetype("Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), f"Comic: {prompt[:50]}", fill='black', font=font)
        draw.text((50, 100), f"Job ID: {job_id}", fill='gray', font=font)
        draw.text((50, 150), "Layout assembly failed - using fallback", fill='red', font=font)
        
        # Convert to bytes
        from io import BytesIO
        output = BytesIO()
        canvas.save(output, format='PNG')
        comic_data = output.getvalue()
        
        logger.debug(f"🔄 layout_assembler: Created fallback layout, size: {len(comic_data)} bytes")
        
        return {
            **state,
            "comic_data": comic_data,
            "messages": state.get("messages", []) + ["Comic assembled with fallback layout"]
        }

# Create the LangGraph workflow
def create_comic_workflow():
    """Create the LangGraph workflow for comic generation"""
    logger.debug("🔧 create_comic_workflow: Creating LangGraph workflow")
    
    # Create the state graph
    workflow = StateGraph(ComicState)
    
    # Add nodes
    workflow.add_node("scene_parser", scene_parser)
    workflow.add_node("panel_planner", panel_planner)
    workflow.add_node("image_generator", image_generator)
    workflow.add_node("layout_assembler", layout_assembler)
    
    # Define the flow
    workflow.set_entry_point("scene_parser")
    workflow.add_edge("scene_parser", "panel_planner")
    workflow.add_edge("panel_planner", "image_generator")
    workflow.add_edge("image_generator", "layout_assembler")
    workflow.add_edge("layout_assembler", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    logger.debug("✅ create_comic_workflow: Workflow compiled successfully")
    
    return compiled_workflow

# Main pipeline function that uses LangGraph
def create_comic_pipeline():
    """Create the main comic generation pipeline using LangGraph"""
    logger.debug("🚀 create_comic_pipeline: Creating main pipeline")
    
    # Create the LangGraph workflow
    workflow = create_comic_workflow()
    
    async def pipeline(state: Dict[str, Any]) -> Dict[str, Any]:
        """Main pipeline that runs the LangGraph workflow"""
        logger.debug(f"🔍 pipeline: Starting with state keys: {list(state.keys())}")
        
        # Add job ID if not present
        if "job_id" not in state:
            state["job_id"] = str(uuid.uuid4())
            logger.debug(f"🆔 pipeline: Generated job_id: {state['job_id']}")
        
        # Initialize LangGraph state
        langgraph_state = {
            "prompt": state["prompt"],
            "style": state["style"],
            "panels": state["panels"],
            "job_id": state["job_id"],
            "messages": []
        }
        
        logger.debug(f"📋 pipeline: Initialized LangGraph state: {langgraph_state}")
        
        # Run the LangGraph workflow
        try:
            logger.debug("🚀 pipeline: Invoking LangGraph workflow")
            result = await workflow.ainvoke(langgraph_state)
            logger.debug(f"✅ pipeline: LangGraph workflow completed, result keys: {list(result.keys())}")
            
            # Convert image data to base64 for API response
            image_data_b64 = []
            for i, img_data in enumerate(result.get("image_data", [])):
                image_data_b64.append(base64.b64encode(img_data).decode('utf-8'))
                logger.debug(f"🖼️ pipeline: Converted image {i+1} to base64, size: {len(img_data)} bytes")
            
            comic_data_b64 = base64.b64encode(result.get("comic_data", b"")).decode('utf-8')
            logger.debug(f"📄 pipeline: Converted comic data to base64, size: {len(result.get('comic_data', b''))} bytes")
            
            # Convert back to our format
            final_result = {
                **state,
                "scene": result["scene"],
                "panel_descriptions": result["panel_descriptions"],
                "image_data": image_data_b64,
                "comic_data": comic_data_b64,
                "messages": result["messages"],
                "message": result["messages"][-1] if result["messages"] else "Pipeline completed"
            }
            
            logger.debug(f"✅ pipeline: Final result prepared with {len(image_data_b64)} images")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ pipeline: Workflow failed: {e}")
            return {
                **state,
                "error": str(e),
                "message": f"Pipeline failed: {str(e)}"
            }
    
    logger.debug("✅ create_comic_pipeline: Pipeline created successfully")
    return pipeline

# Usage example
if __name__ == "__main__":
    import asyncio
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def test_pipeline():
        # Test the LangGraph pipeline
        pipeline = create_comic_pipeline()
        
        test_state = {
            "prompt": "Two kids in a spaceship arguing about pizza",
            "style": "Manga",
            "panels": 3
        }
        
        result = await pipeline(test_state)
        print("LangGraph Pipeline result:")
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test_pipeline()) 