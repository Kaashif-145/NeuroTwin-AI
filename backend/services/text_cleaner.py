import re

def clean_ocr_garbage(text):
    """
    Removes common OCR artifacts, image placeholders, and garbage sequences
    that often plague PDF-to-text extraction.
    """
    if not text:
        return ""
    
    # Remove obvious image placeholders and their subsequent junk
    # e.g., "Picture: X 7 7 / 8 x"
    patterns_to_remove = [
        r"(?i)\[\s*\]\s*intentionally\s*omitted",
        r"(?i)start\s*of\s*picture\s*text",
        r"(?i)end\s*of\s*picture\s*text",
        r"(?i)(?:picture|photo|image|fig|figure)\s*(?:is|not|available|omitted|placeholder|shown)?\s*[:\.]?\s*[X0-9\/\s\.\:]{5,200}",
        r"(?i)pictures\s*intentionally\s*omitted",
        r"(?i)image\s*not\s*available",
        r"!\[.*?\]\(.*?\)", # Remove markdown images
        r"(?:/[a-zA-Z0-9_\-\.\\]+){4,}", # Remove long file paths
        r"(?:[0-9]{1,3}[/\\]){4,}[0-9]{1,3}", # Remove noisy sequences like 7/7/6/7...
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, " ", text)
        
    # Remove sequences of single characters separated by spaces (e.g., "x 7 7 7 / / 7")
    text = re.sub(r"(?:[a-zA-Z0-9\/\*]\s+){5,}", " ", text)
    
    # Nuclear removal for bolding and arrows often found in bad OCR
    text = text.replace("**", " ")
    text = text.replace("==>", " ")
    text = text.replace("<==", " ")
    
    # Remove repetitive symbols
    text = re.sub(r"([\/\\_\|\-\.\=\*])\1{1,}", " ", text)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()

def is_math_expression(text):
    """Basic check to see if a string looks like a mathematical expression."""
    math_symbols = {'=', '+', '-', '*', '/', '^', '(', ')', '∫', '∑', '√', 'π'}
    if any(sym in text for sym in math_symbols):
        # Count alphanumeric vs symbols
        alnum = sum(1 for c in text if c.isalnum())
        symbols = sum(1 for c in text if c in math_symbols)
        if symbols > 0 and (alnum / (symbols + alnum)) < 0.8:
            return True
    return False

def post_process_summary(summary):
    """Cleans up the generated summary to remove hallucinations or artifact leakages."""
    if not summary:
        return ""
        
    # Remove "Pictures intentionally omitted" if it leaked into the summary
    summary = re.sub(r"(?i)pictures\s*intentionally\s*omitted\.?", "", summary)
    summary = re.sub(r"(?i)image\s*restoration\s*service\.?", "", summary)
    
    # Remove junk sequences from summary
    summary = clean_ocr_garbage(summary)
    
    return summary.strip()
