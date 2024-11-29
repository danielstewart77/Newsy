import os
from pydantic import BaseModel, Field
import httpx
import logging
from typing import Optional

from models.article import Article, ArticleDTO
from services.utilities import sanitize_filename

# Set up logging
logger = logging.getLogger(__name__)

# Set the directory to store audio files
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Define the Pydantic model
class TTSRequest(BaseModel):
    voice: str = Field(..., example="southern_english_female-glow_tts:en")
    text: str = Field(..., example="Mom, can I have one of those cinnamon rolls")
    vocoder: Optional[str] = Field("high", example="high")
    denoiserStrength: Optional[float] = Field(0.09, example=0.09, ge=0.0, le=1.0)
    cache: Optional[bool] = Field(False, example=False)

# Define the function to call the API
async def call_tts_api(tts_request: TTSRequest):
    url = "http://localhost:5500/api/tts"
    params = tts_request.model_dump()
    headers = {"accept": "*/*"}
    timeout = httpx.Timeout(30.0)  # Set a custom timeout of 30 seconds
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.content
            else:
                response.raise_for_status()
        except httpx.ReadTimeout:
            logger.error(f"Request timed out for text: {tts_request.text}")
            return None

async def read_news(article: Article) -> str:
    # Create a TTS request and get the audio response
    tts_request = TTSRequest(voice="en-us_mary_ann:en", text=article.body)
    tts_audio = await call_tts_api(tts_request)

    filename = None

    if tts_audio:
        # Save the audio file to disk
        sanitized_title = sanitize_filename(article.title)
        filename = f"{sanitized_title}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(tts_audio)
        
    return filename

# Example usage
# tts_request = TTSRequest(voice="en-us_mary_ann:en", text="Mom, can I have one of those cinnamon rolls", vocoder="high", denoiserStrength=0.09, cache=False)
# audio_content = await call_tts_api(tts_request)
# with open('output.wav', 'wb') as f:
#     f.write(audio_content)
