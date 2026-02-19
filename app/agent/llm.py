import os
import google.generativeai as genai
from app.core.config import settings
from pydantic import BaseModel
import logging

logger = logging.getLogger("agent")

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

def get_model(model_name: str = "gemini-2.5-flash"):
    # Fallback/Default wrapper if needed, but mostly distinct clients now
    return genai.GenerativeModel(model_name)

async def generate_content(prompt: str, model_name: str = "gemini-2.5-flash") -> str:
    model = get_model(model_name)
    response = await model.generate_content_async(prompt)
    return response.text

async def generate_structured_content(prompt: str, response_schema: type[BaseModel], model_name: str = "gemini-2.5-flash"):
    """
    Generates structured content using the specific pattern for Gemini 2.5 Flash / Pro (and newer previews).
    """
    try:
        # If 'response_schema' is a Pydantic model, model_json_schema() gives the dict.
        
        model = genai.GenerativeModel(model_name)
        
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema 
        )
        
        response = await model.generate_content_async(
            prompt, 
            generation_config=generation_config
        )
        return response.text
    except Exception as e:
        logger.error(f"LLM Generation Error: {e}")
        raise
