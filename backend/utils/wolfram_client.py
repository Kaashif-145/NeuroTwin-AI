import os
import requests
from dotenv import load_dotenv

load_dotenv()

WOLFRAM_APP_ID = os.getenv("WOLFRAM_APP_ID", "").strip()

def solve_with_wolfram(query):
    """
    Sends a query to Wolfram Alpha Full Results API.
    Returns a structured summary of the solution.
    """
    if not WOLFRAM_APP_ID or WOLFRAM_APP_ID == "your_api_key_here":
        return None
        
    url = "http://api.wolframalpha.com/v2/query"
    params = {
        "appid": WOLFRAM_APP_ID,
        "input": query,
        "output": "json",
        "format": "plaintext"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("queryresult", {}).get("success", False):
            return "Wolfram Alpha could not solve this specific expression."
            
        pods = data["queryresult"].get("pods", [])
        result_parts = []
        
        for pod in pods:
            title = pod.get("title", "")
            subpods = pod.get("subpods", [])
            for sub in subpods:
                plaintext = sub.get("plaintext", "")
                if plaintext:
                    result_parts.append(f"### {title}\n{plaintext}")
                    
        return "\n\n".join(result_parts[:5]) # Return top 5 informative pods
        
    except Exception as e:
        return f"Error connecting to Wolfram Alpha: {str(e)}"
