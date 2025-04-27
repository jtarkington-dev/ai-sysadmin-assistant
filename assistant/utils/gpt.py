# assistant/utils/gpt.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def ask_gpt(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        print("ERROR: OpenRouter API key not found.")
        return ""

    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openai/gpt-4-turbo",
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as api_error:
        print(f"API request failed: {api_error}")
        return ""
    except (KeyError, IndexError) as parsing_error:
        print(f"Unexpected API response format: {parsing_error}")
        return ""
