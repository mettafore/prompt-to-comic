"""
Simple LLM utilities for the comic pipeline.
"""

import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class LLMClient:
    """Simple LLM client for OpenAI calls"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        logger.debug(f"🧠 LLMClient: Initializing with model={model}")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.debug(f"✅ LLMClient: Initialized successfully")
    
    async def generate(self, prompt: str) -> str:
        """Generate text using OpenAI"""
        logger.debug(f"📝 LLMClient.generate: Sending prompt (length={len(prompt)})")
        logger.debug(f"📝 LLMClient.generate: Prompt preview: {prompt[:100]}...")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.debug(f"✅ LLMClient.generate: Received response (length={len(result)})")
            logger.debug(f"✅ LLMClient.generate: Response preview: {result[:100]}...")
            
            return result
        except Exception as e:
            logger.error(f"❌ LLMClient.generate: OpenAI API error: {e}")
            raise Exception(f"Failed to generate text: {e}")
    
    async def generate_structured(self, prompt: str) -> Dict[str, Any]:
        """Generate structured output using OpenAI"""
        logger.debug(f"📝 LLMClient.generate_structured: Sending structured prompt (length={len(prompt)})")
        logger.debug(f"📝 LLMClient.generate_structured: Prompt preview: {prompt[:100]}...")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns valid JSON."},
                    {"role": "user", "content": f"{prompt}\n\nReturn the response as valid JSON."}
                ],
                max_tokens=1000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            logger.debug(f"✅ LLMClient.generate_structured: Received JSON response (length={len(content)})")
            logger.debug(f"✅ LLMClient.generate_structured: JSON preview: {content[:100]}...")
            
            parsed_result = json.loads(content)
            logger.debug(f"✅ LLMClient.generate_structured: Parsed JSON successfully: {parsed_result}")
            
            return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"❌ LLMClient.generate_structured: JSON parsing error: {e}")
            logger.error(f"❌ LLMClient.generate_structured: Raw content: {content}")
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
            logger.error(f"❌ LLMClient.generate_structured: OpenAI API error: {e}")
            raise Exception(f"Failed to generate structured output: {e}")

# Global LLM client instance
llm_client = None

def get_llm_client(api_key: str = None) -> LLMClient:
    """Get or create LLM client instance"""
    global llm_client
    logger.debug(f"🔍 get_llm_client: Requested LLM client")
    
    if llm_client is None:
        if api_key is None:
            logger.error("❌ get_llm_client: No API key provided")
            raise Exception("OpenAI API key required")
        
        logger.debug("🔧 get_llm_client: Creating new LLM client instance")
        llm_client = LLMClient(api_key=api_key)
        logger.debug("✅ get_llm_client: LLM client created successfully")
    else:
        logger.debug("✅ get_llm_client: Returning existing LLM client instance")
    
    return llm_client 