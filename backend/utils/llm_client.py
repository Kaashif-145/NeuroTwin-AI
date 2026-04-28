import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

from backend.utils.gemini_client import get_gemini_response
from backend.utils.openai_client import get_openai_response
from backend.utils.wolfram_client import solve_with_wolfram

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


def is_math_query(text):
    """Basic heuristic to detect if a query is mathematical, excluding coding requests."""
    text_lower = text.lower()
    
    # If it looks like a code analysis or programming request, it's NOT a math query for Wolfram
    if any(k in text_lower for k in ['analyze', 'code', 'refactor', 'programming', 'script']):
        return False
        
    math_indicators = ['solve', 'calculate', 'derivative', 'integral', 'equation', 'simplify', 'limit of']
    has_indicator = any(ind in text_lower for ind in math_indicators)
    has_symbols = any(sym in text for sym in ['=', '+', '-', '*', '/', '^', '∫', '∑', '√'])
    
    # Ensure it's not a block of code (heuristic: presence of triple backticks or many semicolons/braces)
    if '```' in text or text.count(';') > 5 or text.count('{') > 5:
        return False
        
    return has_indicator or has_symbols


def _history_to_messages(history, prompt, system_prefix):
    messages = [{"role": "system", "content": system_prefix}]

    for item in history or []:
        role = item.get("role", "user")
        content_parts = item.get("parts", [])
        if isinstance(content_parts, list):
            content = "\n".join(str(part) for part in content_parts)
        else:
            content = str(content_parts)
        messages.append(
            {
                "role": "assistant" if role == "model" else "user",
                "content": content,
            }
        )

    messages.append({"role": "user", "content": prompt})
    return messages


def get_ollama_response(prompt, history=None, system_prefix="You are a helpful study assistant."):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": _history_to_messages(history, prompt, system_prefix),
        "stream": False,
    }

    request = urllib.request.Request(
        f"{OLLAMA_URL.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Ollama HTTP error {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Ollama is not reachable at {OLLAMA_URL}. Start Ollama and run `ollama serve` if needed."
        ) from e

    message = raw.get("message", {})
    content = message.get("content", "").strip()
    if not content:
        raise RuntimeError("Ollama returned an empty response.")
    return content


def get_chat_response(
    prompt,
    history=None,
    system_prefix="You are NeuroTwin — an expert AI study assistant for students. Be concise, clear, and educational.",
    allow_wolfram=True
):
    errors = []
    
    # Priority 0: Wolfram Alpha (Only if allowed and detected as math)
    if allow_wolfram and is_math_query(prompt):
        try:
            wolfram_res = solve_with_wolfram(prompt)
            if wolfram_res and "Error" not in wolfram_res and "could not solve" not in wolfram_res.lower():
                return wolfram_res, "wolfram"
        except:
            pass # Fall through on any wolfram error

    # Priority 1: Gemini (FASTEST & ROTATED)
    try:
        return get_gemini_response(prompt=prompt, history=history, system_prefix=system_prefix), "gemini"
    except Exception as e:
        errors.append(f"Gemini: {e}")

    # Priority 2: OpenAI
    openai_res = get_openai_response(prompt=prompt, history=history, system_prefix=system_prefix)
    if openai_res:
        if not openai_res.startswith("OpenAI Error"):
            return openai_res, "openai"
        else:
            errors.append(f"OpenAI: {openai_res}")

    try:
        return get_ollama_response(prompt=prompt, history=history, system_prefix=system_prefix), "ollama"
    except Exception as e:
        errors.append(f"Ollama: {e}")

    raise RuntimeError(
        "❌ **All AI Services Unavailable**\n\n" + 
        "\n".join([f"• {err}" for err in errors]) + 
        "\n\n**Suggestions:**\n"
        "1. Check your OpenAI balance/key.\n"
        "2. Add more Gemini keys to .env.\n"
        "3. Start Ollama locally."
    )
