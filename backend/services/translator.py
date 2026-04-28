from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# M2M100 is excellent for many-to-many translation including Hindi and Punjabi
MODEL_NAME = "facebook/m2m100_418M"

try:
    model = M2M100ForConditionalGeneration.from_pretrained(MODEL_NAME)
    tokenizer = M2M100Tokenizer.from_pretrained(MODEL_NAME)
except Exception as e:
    print(f"Error loading Translation model: {e}")
    model = None
    tokenizer = None

def translate_text(text, target_lang="hi"):
    """
    target_lang codes: 'hi' (Hindi), 'pa' (Punjabi), 'en' (English), etc.
    """
    if not model or not tokenizer:
        return text # Fallback to original
    
    # Set source language to English
    tokenizer.src_lang = "en"
    encoded_en = tokenizer(text, return_tensors="pt")
    
    # Generate translation
    generated_tokens = model.generate(**encoded_en, forced_bos_token_id=tokenizer.get_lang_id(target_lang))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
