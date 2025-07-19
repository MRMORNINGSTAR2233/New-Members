from typing import Any, Dict, List, Optional

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


# Configure the Google Generative AI SDK
genai.configure(api_key=settings.GEMINI_API_KEY)

# Create LangChain model instance with Gemini 1.5 Flash
gemini_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    top_p=0.95,
    top_k=40,
    max_output_tokens=2048,
    safety_settings=[
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ],
    streaming=False,
    convert_system_message_to_human=True
)
