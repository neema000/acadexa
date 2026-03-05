# backend/llm/voice_interpreter.py
import os
import json
import re
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")  # Fastest: 1.1B params
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"  # Enabled by default

# Optimized for 5-7 second response
DEFAULT_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "10"))  # Allow up to 10s
HEALTH_CHECK_TIMEOUT = 0.5  # Quick check


SYSTEM_PROMPT = """Intent classifier for LMS. Return JSON: {"intent": "<string>", "slots": {}, "confidence": 0.0, "needs_clarification": false, "clarifying_question": ""}.

Intents: show_my_attendance, show_my_attendance_course, show_my_cgpa, show_my_courses, show_my_result, list_students, list_courses, list_teachers, list_enrollments_for_student, unknown.

Rules: attendance summary=show_my_attendance, attendance+course=show_my_attendance_course+slots.course_code, unsure=unknown."""


def _clean_json(text: str) -> dict:
    """
    Ollama sometimes returns extra text. Extract first JSON object.
    """
    if not text:
        return {}
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


async def is_ollama_available() -> bool:
    """
    Quick health check to see if Ollama is running.
    Returns False if Ollama is unreachable within 2 seconds.
    """
    try:
        timeout = httpx.Timeout(HEALTH_CHECK_TIMEOUT)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def interpret_with_ollama(command: str, role: str, user_context: dict):
    """
    Returns (llm_json, raw_text)
    """
    prompt = f"Role: {role}\nCommand: {command}\nReturn JSON only."

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "format": "json",
        "keep_alive": "5m",  # Keep model loaded in memory for 5 minutes
        "options": {
            "temperature": 0.0,
            "num_predict": 64,  # Minimal tokens for JSON response
            "top_k": 5,  # Very focused sampling
            "top_p": 0.3,  # Fast greedy sampling
            "num_ctx": 256,  # Minimal context window
            "num_gpu": 1,  # Use GPU if available
            "num_thread": 4,  # Optimize CPU threads
        },
    }

    timeout = httpx.Timeout(DEFAULT_TIMEOUT, connect=2.0)

    async def _call_once():
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
            raw = data.get("response", "")  # Ollama returns "response"
            llm_json = _clean_json(raw) or {}
            # normalize defaults
            llm_json.setdefault("intent", "unknown")
            llm_json.setdefault("slots", {})
            llm_json.setdefault("confidence", 0.0)
            llm_json.setdefault("needs_clarification", False)
            llm_json.setdefault("clarifying_question", "")
            return llm_json, raw

    # Single attempt with no retry to avoid double wait time
    try:
        return await _call_once()
    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException):
        # Don't retry on timeout - fail fast
        raise Exception("LLM timeout")
    except Exception as e:
        # Any other error - fail fast
        raise Exception(f"LLM error: {str(e)[:50]}")
