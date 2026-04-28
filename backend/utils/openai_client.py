import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

def get_openai_response(prompt, history=None, system_prefix="You are a helpful study assistant."):
    """
    Sends a prompt to OpenAI's GPT-4o-mini or GPT-4o.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_api_key_here":
        return "OpenAI Error: No API key found in .env file."
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    messages = [{"role": "system", "content": system_prefix}]
    
    if history:
        for msg in history:
            role = "assistant" if msg["role"] == "model" else "user"
            content = "\n".join(msg["parts"]) if isinstance(msg["parts"], list) else str(msg["parts"])
            messages.append({"role": role, "content": content})
            
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        if response.status_code != 200:
            return f"OpenAI Error: Status {response.status_code} - {response.text}"
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"OpenAI Error: {str(e)}"
