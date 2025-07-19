from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings


@dataclass
class GeminiConfig:
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 2048


def initialize_gemini_model(api_key: str, model_name: str, config: GeminiConfig):
    """Initialize the Gemini model with the given API key and configuration."""
    # Configure the Google Generative AI SDK
    genai.configure(api_key=api_key)
    
    # Create the model
    model = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=config.temperature,
        top_p=config.top_p,
        top_k=config.top_k,
        max_output_tokens=config.max_output_tokens,
        google_api_key=api_key,  # Pass API key directly
        convert_system_message_to_human=True,
    )
    
    return model


def get_gemini_model():
    """Get the configured Gemini model, creating it if necessary."""
    config = GeminiConfig(
        temperature=settings.GEMINI_TEMPERATURE if hasattr(settings, 'GEMINI_TEMPERATURE') else 0.7,
        top_p=settings.GEMINI_TOP_P if hasattr(settings, 'GEMINI_TOP_P') else 0.95,
        top_k=settings.GEMINI_TOP_K if hasattr(settings, 'GEMINI_TOP_K') else 40,
        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS if hasattr(settings, 'GEMINI_MAX_OUTPUT_TOKENS') else 2048,
    )
    
    model_name = settings.GEMINI_MODEL if hasattr(settings, 'GEMINI_MODEL') else "gemini-1.5-flash"
    
    return initialize_gemini_model(settings.GEMINI_API_KEY, model_name, config)


# Create the model instance
gemini_model = get_gemini_model()
