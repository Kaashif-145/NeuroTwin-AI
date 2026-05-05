# M2M100 is excellent but heavy. We use lazy loading or LLM fallback.
MODEL_NAME = "facebook/m2m100_418M"
model = None
tokenizer = None

def _get_translator_model():
    global model, tokenizer
    if model is None or tokenizer is None:
        try:
            from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
            model = M2M100ForConditionalGeneration.from_pretrained(MODEL_NAME)
            tokenizer = M2M100Tokenizer.from_pretrained(MODEL_NAME)
        except Exception as e:
            print(f"Translator model load skipped: {e}")
    return model, tokenizer

def translate_text(text, target_lang="hi"):
    """
    target_lang codes: 'hi' (Hindi), 'pa' (Punjabi), 'en' (English), etc.
    """
    md, tk = _get_translator_model()
    if not md or not tk:
        # Fallback to LLM if available
        try:
            from backend.utils.llm_client import get_chat_response
            prompt = f"Translate the following text to language code '{target_lang}':\n\n{text}"
            translated, _ = get_chat_response(prompt)
            if translated and not translated.startswith("Error"):
                return translated
        except:
            pass
        return text # Ultimate fallback
    
    # Set source language to English
    tk.src_lang = "en"
    encoded_en = tk(text, return_tensors="pt")
    
    # Generate translation
    generated_tokens = md.generate(**encoded_en, forced_bos_token_id=tk.get_lang_id(target_lang))
    return tk.batch_decode(generated_tokens, skip_special_tokens=True)[0]
