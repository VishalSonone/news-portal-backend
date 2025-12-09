import requests
from app.core.config import settings
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = settings.GROQ_API_KEY


def summarize_news(text: str) -> str:
  
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    model_name = "llama-3.3-70b-versatile"

    prompt = (
        "Summarize the following news article in a concise, factual way without "
        "adding opinions or speculation:\n\n" + text
    )

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You summarize news articles accurately."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()

    summary = data["choices"][0]["message"]["content"]
    return summary.strip()
