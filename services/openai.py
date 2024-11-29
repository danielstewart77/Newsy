import os
import logging
import json

from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(dotenv_path="secrets.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def structured_chat_completion(text: str, llm_model: str, feature_model: BaseModel) -> BaseModel:
    completion = client.beta.chat.completions.parse(
        model=llm_model,
        messages=[
            {"role": "system", "content": "Extract the news artcles from this text"},
            {"role": "user", "content": json.dumps(text)},
        ],
        response_format=feature_model
    )
    return completion.choices[0].message.parsed