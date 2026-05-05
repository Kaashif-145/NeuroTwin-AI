import re
from backend.utils.llm_client import get_chat_response
from backend.services.text_cleaner import clean_ocr_garbage

def extract_key_details(text):
    """
    Extracts high-priority key details, facts, and insights from the document text
    using high-fidelity LLM analysis.
    """
    if not text:
        return []
        
    # Clean text first
    clean_text = clean_ocr_garbage(text)
    
    # Use LLM for intelligent extraction
    system_prompt = (
        "You are an expert academic research assistant. Extract exactly 7-10 high-priority key details in ENGLISH, "
        "fundamental facts, or critical insights from the following text. "
        "Each detail should be a single, impactful sentence in English. "
        "Avoid any OCR noise, file paths, or image placeholders. "
        "Return the details as a simple bulleted list with no introduction."
    )
    
    try:
        # Use a significant chunk of text (up to 8000 chars) for detail extraction
        context = clean_text[:8000]
        response, provider = get_chat_response(
            prompt=f"Extract key details from this study material:\n\n{context}",
            system_prefix=system_prompt
        )
        
        # Parse bullet points
        details = [line.strip('- *').strip() for line in response.splitlines() if line.strip()]
        return details[:10]
        
    except Exception as e:
        print(f"LLM Key Detail extraction failed: {e}. Falling back to rule-based.")
        # Rule-based fallback: Extract sentences with high information density
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if 60 < len(s.strip()) < 200]
        # Heuristic: Priority to sentences with dates, percentages, or key terms
        key_indicators = ['important', 'significant', 'result', 'because', 'due to', '%', '202', 'established']
        ranked = []
        for s in sentences:
            score = sum(2 for ind in key_indicators if ind in s.lower())
            if score > 0:
                ranked.append((score, s))
        
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in ranked[:8]]

def extract_actionable_insights(text):
    """
    Extracts actionable study insights or 'takeaways'.
    """
    system_prompt = (
        "Identify 3-5 actionable study takeaways or 'Must-Know' insights from this text in ENGLISH. "
        "Format as a list of short, punchy points in English."
    )
    try:
        context = text[:5000]
        response, _ = get_chat_response(prompt=context, system_prefix=system_prompt)
        return [line.strip('- *').strip() for line in response.splitlines() if line.strip()][:5]
    except:
        return ["Focus on core definitions.", "Review mathematical derivations.", "Connect concepts to practical examples."]
