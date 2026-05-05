import re

# Heavy imports (torch, transformers) are now moved inside functions to prevent startup crashes.
from backend.services.text_cleaner import clean_ocr_garbage, post_process_summary
from backend.utils.llm_client import get_chat_response

# Using a distilled, much faster model for demonstration purposes
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# Using a distilled, much faster model for demonstration purposes
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
MAX_SOURCE_CHARS = 12000
CHUNK_SIZE = 2200
CHUNK_OVERLAP = 250

# We now use lazy loading or Ollama/Gemini via llm_client to save memory
tokenizer = None
model = None

def _get_local_model():
    """Lazy loads the local model only if needed and if RAM is available."""
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            # Only attempt to load if explicitly requested or if LLM API fails
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        except Exception as e:
            print(f"Local model load skipped/failed: {e}")
    return tokenizer, model


def clean_text_symbols(text):
    if not isinstance(text, str):
        return ""
    
    # Fix common symbols that often appear as boxes or junk
    mappings = {
        "\x00": " ", "\x01": " ", "\x02": " ", "\x03": " ", "\x04": " ", "\x05": " ",
        "\x06": " ", "\x07": " ", "\x08": " ", "\x0b": " ", "\x0c": " ", "\x0e": " ",
        "\x0f": " ", "\x10": " ", "\x11": " ", "\x12": " ", "\x13": " ", "\x14": " ",
        "\x15": " ", "\x16": " ", "\x17": " ", "\x18": " ", "\x19": " ", "\x1a": " ",
        "\x1b": " ", "\x1c": " ", "\x1d": " ", "\x1e": " ", "\x1f": " ",
        "\uf0d8": "->", "\uf0fc": "chk", "\uf07a": ">", "\uf0b7": "-", 
        "\uf0a8": "<", "\uf0a9": ">", "\uf071": "!", "\uf020": " ",
        "\uf02d": "(book)", "\uf0e0": "(mail)", "\u2022": "-", "\u25cf": "-",
        "\u25cb": "-", "\u25aa": "-", "\u00b7": "-",
        # Math symbols common in engineering PDFs
        "∫": "integral", "∑": "sum", "≈": "approx", "≤": "<=", "≥": ">=",
        "±": "+/-", "→": "->", "∞": "inf", "π": "pi", "θ": "theta", "φ": "phi",
        "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "Δ": "Delta",
        "∇": "nabla", "∈": "in", "≠": "!=", "λ": "lambda", "μ": "mu", "σ": "sigma",
        "ω": "omega", "×": "*", "÷": "/", "√": "sqrt", "²": "^2", "³": "^3",
        "⊠": " ", "□": " ", # Catch literal bad characters
    }
    
    for search, replace in mappings.items():
        text = text.replace(search, replace)
        
    # Catch Private Use Area characters and other mathematical junk
    def _is_safe(c):
        o = ord(c)
        if 32 <= o <= 126: return True # Standard ASCII
        if o in (9, 10, 13): return True # tab, newline, carriage return
        if 0x00A0 <= o <= 0x024F: return True # Latin Extended
        if 0x0370 <= o <= 0x03FF: return True # Greek
        if 0x2000 <= o <= 0x206F: return True # General Punctuation
        if 0x2200 <= o <= 0x22FF: return True # Mathematical Operators
        return False

    text = "".join(ch if _is_safe(ch) else " " for ch in text)
    
    # Post-processing for specific fraction/box artifacts seen in screenshots
    text = re.sub(r'(\d)\s*\s*\s*', r'\1 / ', text) # Fix fractions that became box-junk
    text = re.sub(r'\s{3,}', ' ', text)
    text = re.sub(r'\*\*+\s*\*+', '', text)
    text = re.sub(r'\[\^\]', '', text)
    return text.strip()

def sanitize_source_text(text):
    if not isinstance(text, str):
        return ""

    text = clean_text_symbols(text)
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)

    filtered_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            filtered_lines.append("")
            continue

        lowered = line.lower()
        # Skip garbage lines or overly repetitive symbols
        if len(line) < 3 and not line.isalnum():
            continue
            
        if (
            lowered.startswith("author:")
            or lowered.startswith("written by:")
            or lowered.startswith("prepared by:")
            or lowered.startswith("professor:")
            or lowered.startswith("instructor:")
            or lowered.startswith("teacher:")
        ):
            continue

        filtered_lines.append(line)

    cleaned = "\n".join(filtered_lines)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    # Strip any residual HTML tags
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    
    # Final pass with specialized OCR cleaner
    cleaned = clean_ocr_garbage(cleaned)
    
    return cleaned.strip()


def _split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _generate_model_summary(text, max_length=150, min_length=50):
    # Try high-fidelity LLM first (OpenAI/Gemini)
    try:
        prompt = f"Summarize the following academic text concisely in ENGLISH (between {min_length} and {max_length} words). Focus on key concepts and definitions:\n\n{text}"
        summary, provider = get_chat_response(prompt, system_prefix="You are a professional academic summarizer. Always respond in English.")
        if summary and not summary.startswith("OpenAI Error") and not summary.startswith("Gemini Error"):
            return summary
    except:
        pass # Fall back to local model

    import torch
    tk, md = _get_local_model()
    if tk is None or md is None:
        return text[:max_length*5]

    inputs = tk([text], max_length=1024, return_tensors="pt", truncation=True)

    with torch.no_grad():
        summary_ids = md.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=max_length,
            min_length=min_length,
            no_repeat_ngram_size=3,
            length_penalty=1.6,
            early_stopping=True,
        )

    return tk.batch_decode(
        summary_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()


def extract_key_features(summary, topics, limit=6):
    features = []
    summary_sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", summary or "")
        if len(s.strip()) > 40
    ]

    for sentence in summary_sentences[:limit]:
        features.append(sentence)

    for topic in topics:
        if len(features) >= limit:
            break
        if not any(topic.lower() in feature.lower() for feature in features):
            features.append(f"Core focus area: {topic}")

    return features[:limit]


def extract_equations(text, limit=12):
    clean_text = sanitize_source_text(text)
    equation_patterns = [
        r"\$[^$]+\$",
        r"\\\([^)]+\\\)",
        r"\\\[[^\]]+\\\]",
        r"(?:[a-zA-Z0-9_]+\s*[\+\-\*\/^]\s*)+[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+", # Simple algebraic: a + b = c
        r"[A-Za-z][A-Za-z0-9_()^]*\s*=\s*[^.\n;]{3,180}",
        r"[^.\n]{0,80}[0-9A-Za-z()]+(?:\s*[\+\-\*/^]\s*[0-9A-Za-z()]+){1,8}\s*=\s*[^.\n]{1,120}",
        r"(?:sin|cos|tan|log|ln|lim|sqrt)\s*\([^)\n]+\)\s*(?:=\s*[^.\n;]{1,120})?",
        r"[^.\n]{0,80}(?:∫|∑|√|π|θ|α|β|λ|μ|σ|Δ|≤|≥|≈)[^.\n]{1,120}",
    ]

    equations = []
    seen = set()
    for pattern in equation_patterns:
        for match in re.findall(pattern, clean_text, flags=re.MULTILINE):
            equation = re.sub(r"\s+", " ", match).strip(" .;:,")
            if len(equation) < 4:
                continue
            key = equation.lower()
            if key in seen:
                continue
            
            # Additional validation: must contain at least one operator or equals sign
            if not any(op in equation for op in ['=', '+', '-', '*', '/', '^', '∫', '∑', '√']):
                continue
                
            seen.add(key)
            equations.append(equation)
            if len(equations) >= limit:
                return equations

    return equations


def generate_summary(text):
    clean_text = sanitize_source_text(text)
    if not clean_text:
        return "Summarization service temporarily unavailable (empty source text)."

    # We prioritize the LLM client (Ollama/Gemini) over the local heavy model
    # The _generate_model_summary function handles the fallback logic.

    clean_text = clean_text[:MAX_SOURCE_CHARS]
    chunks = _split_into_chunks(clean_text)
    chunk_summaries = []

    for chunk in chunks[:5]:
        chunk_summary = _generate_model_summary(chunk, max_length=190, min_length=70)
        if chunk_summary:
            chunk_summary = post_process_summary(chunk_summary)
            chunk_summaries.append(chunk_summary)

    if not chunk_summaries:
        return "Summarization service temporarily unavailable (generation failure)."

    if len(chunk_summaries) == 1:
        final_summary = chunk_summaries[0]
    else:
        combined = " ".join(chunk_summaries)
        final_summary = _generate_model_summary(combined[:4000], max_length=320, min_length=140) or combined
        final_summary = post_process_summary(final_summary)

    detailed_parts = []
    summary_sentences = [
        s.strip() for s in re.split(r"(?<=[.!?])\s+", final_summary) if s.strip()
    ]
    if summary_sentences:
        detailed_parts.append("Overview:\n" + " ".join(summary_sentences[:3]))
        if len(summary_sentences) > 3:
            detailed_parts.append("Detailed Discussion:\n" + " ".join(summary_sentences[3:]))

    equations = extract_equations(clean_text, limit=5)
    if equations:
        equation_lines = "\n".join(f"- {eq}" for eq in equations)
        detailed_parts.append("Important Equations:\n" + equation_lines)

    return "\n\n".join(detailed_parts) if detailed_parts else final_summary


def generate_glossary(topics, context):
    glossary = {}
    clean_context = sanitize_source_text(context)
    # Split specifically on sentence endings and clean up
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_context.replace("\n", " "))]
    
    for topic in topics[:12]:
        topic_lower = topic.lower()
        found_def = False
        for sentence in sentences:
            # Check if topic is in sentence and skip noisy technical headers
            if topic_lower in sentence.lower() and len(sentence.split()) > 4:
                if "--- Content from" in sentence or "Image Restoration" in sentence[:20]:
                    continue
                
                # Limit description length to keep glossary clean
                words = sentence.split()
                if len(words) > 35:
                    definition = " ".join(words[:32]) + "..."
                else:
                    definition = sentence
                
                glossary[topic] = definition
                found_def = True
                break
        
        if not found_def:
            glossary[topic] = "A specialized concept analyzed from the document's core content."

    return glossary
