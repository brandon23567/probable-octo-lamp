import os
from google import genai
from google.genai import types
from app.core.config import settings
from pydantic import BaseModel
import logging
from fastapi import HTTPException, status

logger = logging.getLogger("agent")

# Configure Gemini
# genai.configure(api_key=settings.GOOGLE_API_KEY)

google_gemini_client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)

def get_model(model_name: str = "gemini-3-flash-preview"):
    # Fallback/Default wrapper if needed, but mostly distinct clients now
    return genai.GenerativeModel(model_name)

# async def generate_content(prompt: str, model_name: str = "gemini-3-flash-preview") -> str:
#     response = await google_gemini_client.models.generate_content(
#         model=model_name,
#         contents=prompt
#     )
    
#     return response.text

async def generate_structured_content(prompt: str, response_schema: type[BaseModel], model_name: str = "gemini-3-flash-preview"):
    """
    Generates structured content using the specific pattern for gemini-3-flash-preview.
    """
    try:
        response = await google_gemini_client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a JSON generator. Output only the JSON requested",
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        )

        return response.parsed
    
    except Exception as e:
        logger.error(f"LLM Generation Error: str({e})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate structered content from gemini api"
        )
