import os
import json
import httpx
from typing import Any, Dict

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")  # change if needed


async def ollama_chat(prompt: str) -> str:
    """
    Calls Ollama /api/chat and returns raw assistant content.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()

    # Ollama returns: { message: { role: "...", content: "..." }, ... }
    return data.get("message", {}).get("content", "").strip()


def safe_json_loads(text: str) -> Dict[str, Any]:
    """
    LLM sometimes wraps JSON in ```...``` — strip that safely.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        # Sometimes starts with "json\n{...}"
        cleaned = cleaned.replace("json\n", "", 1).strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        # Try to extract first {...} block
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise
