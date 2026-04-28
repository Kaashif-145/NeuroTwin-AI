"""
gemini_client.py
----------------
Shared Gemini API key rotation utility for NeuroTwin AI.

Loads up to 5 keys from .env (GEMINI_API_KEY, GEMINI_API_KEY_2 ... GEMINI_API_KEY_5).
On every 429 / daily quota error, it automatically rotates to the next key + model
combination so the app never goes dark mid-session.

Usage:
    from backend.utils.gemini_client import get_gemini_response

    reply = get_gemini_response(prompt="Explain Newton's laws", history=[...])
"""

import os
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Models ordered by free-tier quota (highest first)
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",   # 200 req/day, 30 RPM
    "gemini-2.0-flash",        # 200 req/day, 15 RPM
    "gemini-1.5-flash",        # 15 RPM, 1M TPM (Great fallback)
]

def _load_api_keys() -> list[str]:
    """Collect all non-empty API keys defined in the environment."""
    keys = []
    # Primary key
    primary = os.getenv("GEMINI_API_KEY", "").strip()
    if primary and primary != "your_api_key_here":
        keys.append(primary)

    # Extra keys: GEMINI_API_KEY_2 … GEMINI_API_KEY_5
    for i in range(2, 6):
        k = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
        if k and k != "your_api_key_here":
            keys.append(k)
    return keys


def _is_quota_error(err: Exception) -> bool:
    """Return True if the error indicates a rate / daily quota exhaustion."""
    msg = str(err).lower()
    return any(
        token in msg
        for token in ["429", "perday", "per_day", "daily", "quota", "resource_exhausted"]
    )


def _extract_retry_delay(err: Exception, fallback: float = 15.0) -> float:
    """Try to parse the suggested retry delay from the error message."""
    try:
        match = re.search(r"retry[_ ](?:after|in)\D*([\d.]+)\s*s", str(err), re.IGNORECASE)
        if match:
            return float(match.group(1)) + 1
    except Exception:
        pass
    return fallback


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_gemini_response(
    prompt: str,
    history: list[dict] | None = None,
    system_prefix: str = "You are NeuroTwin — an expert AI study assistant for students. Be concise, clear, and educational.",
    max_retries_per_combo: int = 2,
) -> str:
    """
    Send a prompt to Gemini with automatic key + model rotation on quota errors.

    Parameters
    ----------
    prompt              : The user's message / full prompt string.
    history             : List of {"role": "user"|"model", "parts": [str]} dicts.
    system_prefix       : System instruction prepended to the prompt.
    max_retries_per_combo: How many times to retry a single key+model pair on
                          transient rate limits before rotating.

    Returns
    -------
    str — The model's text response.

    Raises
    ------
    RuntimeError — if ALL key+model combinations are exhausted.
    """
    api_keys = _load_api_keys()
    if not api_keys:
        raise RuntimeError(
            "No Gemini API key found. Add GEMINI_API_KEY (and optionally "
            "GEMINI_API_KEY_2 … GEMINI_API_KEY_5) to your .env file."
        )

    full_prompt = f"[{system_prefix}]\n\nStudent Ask: {prompt}"
    history = history or []
    last_error: Exception | None = None

    for i, api_key in enumerate(api_keys):
        # Log to terminal so the developer can see the rotation happening
        print(f"🔄 Rotating to Gemini Key {i+1}...")
        genai.configure(api_key=api_key)

        for model_name in GEMINI_MODELS:
            for attempt in range(max_retries_per_combo):
                try:
                    print(f"   🤖 Trying model: {model_name} (Attempt {attempt+1})")
                    model = genai.GenerativeModel(model_name)
                    chat = model.start_chat(history=history)
                    response = chat.send_message(full_prompt)
                    return response.text  # ✅ Success
                except Exception as e:
                    last_error = e
                    err_str = str(e).lower()

                    if "404" in err_str or "not found" in err_str:
                        print(f"   ❌ Model {model_name} not available for this key. Skipping.")
                        break 

                    if _is_quota_error(e):
                        print(f"   ⚠️ Quota reached for Key {i+1}. Rotating...")
                        time.sleep(2) # Brief pause before rotating to next key
                        break # Rotate to next key/model
                    elif "api_key_invalid" in err_str or "400" in err_str:
                        print(f"   ❌ Key {i+1} is INVALID. Please check .env")
                        break
                    else:
                        print(f"   ❌ Unexpected Error: {err_str}")
                        raise 

    # All keys and models exhausted
    error_msg = (
        "⚠️ All Gemini API keys and models have reached their quota limits.\n\n"
        f"Last Error Detail: {last_error}"
    )
    raise RuntimeError(error_msg)
