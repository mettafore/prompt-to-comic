#!/usr/bin/env python3
"""
Simple test to verify real AI is working.
"""

import os
import asyncio
from dotenv import load_dotenv
from app.utils.llm import get_llm_client

async def test_llm():
    """Test LLM functionality"""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    print("✅ API key found")
    
    try:
        llm_client = get_llm_client(api_key)
        
        # Test simple generation
        response = await llm_client.generate("Say hello in one word")
        print(f"✅ LLM test: {response}")
        
        # Test structured generation
        structured = await llm_client.generate_structured('{"message": "hello"}')
        print(f"✅ Structured test: {structured}")
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm()) 