import os
import time
from pathlib import Path
from typing import Dict, Optional

import requests

# Try to load from .env file if it exists
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    with open(_env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)


def generate_response(
    model_name: str,
    system_prompt: str,
    user_content: str,
    temperature: float = 0.7,
    seed: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict:
    """
    Calls OpenRouter API to generate a response.

    Args:
        model_name: OpenRouter model identifier (e.g., "meta-llama/llama-3.1-8b-instruct")
        system_prompt: System prompt for the model
        user_content: User message content
        temperature: Sampling temperature (default: 0.7)
        seed: Optional random seed for reproducibility
        api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)

    Returns:
        Dict with:
        - text: the model's response string
        - raw: raw API response metadata (usage, model info, etc.)
    """
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
            "or pass api_key parameter."
        )

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo/llm-bias-research",  # Optional: for tracking
        "X-Title": "LLM Bias Research",  # Optional: for tracking
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
    }

    if seed is not None:
        payload["seed"] = seed

    # Make API call with retry logic
    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            data = response.json()

            # Extract response text
            if "choices" in data and len(data["choices"]) > 0:
                response_text = data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected API response format: {data}")

            return {
                "text": response_text,
                "raw": {
                    "usage": data.get("usage"),
                    "model": data.get("model"),
                    "id": data.get("id"),
                    "created": data.get("created"),
                    "provider": data.get("provider"),
                },
            }

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(
                    f"API request failed (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                raise RuntimeError(
                    f"OpenRouter API call failed after {max_retries} attempts: {e}"
                ) from e

