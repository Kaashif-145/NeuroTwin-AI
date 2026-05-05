# Heavy imports (torch, transformers) are now moved inside functions to prevent startup crashes.
import random
import re
import os
import json
from backend.services.text_cleaner import clean_ocr_garbage
from backend.utils.llm_client import get_chat_response

# Model for Question Generation
QG_MODEL = "mrm8488/t5-base-finetuned-question-generation-ap"

# We prioritize LLM (Ollama/Gemini) or rule-based fallback to save memory
tokenizer = None
model = None

def _get_qg_model():
    """Lazy loads the question generation model only if needed."""
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            tokenizer = AutoTokenizer.from_pretrained(QG_MODEL)
            model = AutoModelForSeq2SeqLM.from_pretrained(QG_MODEL)
        except Exception as e:
            print(f"QG model load skipped: {e}")
    return tokenizer, model

def fallback_generate_quiz(text, sentences):
    """
    Simpler NLP-based fallback for generating questions if the T5 model fails.
    """
    q_set = []
    random.shuffle(sentences)
    for s in sentences[:15]:
        words = s.split()
        if len(words) < 5: continue
        
        # Simple blank-filling question
        idx = random.randint(0, len(words) - 1)
        answer = words[idx].strip('.,!?:;()')
        if len(answer) < 3: continue
        
        question = s.replace(answer, "_______")
        distractors = random.sample(["concept", "data", "result", "process", "detail", "method"], 3)
        options = list(set(distractors + [answer]))
        random.shuffle(options)
        
        q_set.append({"question": f"Fill in the blank: {question}", "options": options, "answer": answer})
    return q_set

def generate_descriptive_paper(text):
    """
    Generates a formal exam paper with 5, 10, and 15 marks descriptive questions and an answer key.
    """
    # Broadened math detection to catch algebraic structures, equals signs with variables, and common notation
    is_math_heavy = bool(re.search(r'(\$.+?\$|\\[a-zA-Z]+|∫|∑|∈|≈|≤|≥|[a-zA-Z]\([a-zA-Z]\)\s*=|[0-9a-zA-Z]+\s*[\+\-\*\/]\s*[0-9a-zA-Z]+\s*=)', text))
    
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 150]
    if len(paragraphs) < 3:
        paragraphs = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if len(s.strip()) > 50]

    paper = []
    
    # Shuffle paragraphs to avoid getting stuck in prefaces/acknowledgements at the start of books
    if len(paragraphs) > 10:
        # Skip the first 10% which is usually preface/intro for large textbooks
        content_paras = paragraphs[len(paragraphs)//10:]
        random.shuffle(content_paras)
    else:
        content_paras = list(paragraphs)
        random.shuffle(content_paras)
        
    # Mathematical Equations extraction
    equations = re.findall(r'(\$.+?\$|[a-zA-Z]\([a-z]\)\s*=.*?|[a-zA-Z0-9]+\s*[\+\-\*\/]\s*[a-zA-Z0-9]+\s*=.*?$)', text, re.MULTILINE)
    if equations: random.shuffle(equations)
    
    # Stopwords to explicitly prevent bad blank definitions
    stopwords = {'this', 'that', 'these', 'those', 'there', 'they', 'here', 'what', 'when'}
    
    # 1. 5-Mark Questions (Target 4)
    for i, p in enumerate(content_paras[:4]):
        if is_math_heavy and equations and len(equations) > i:
            eq = equations[i].strip()
            if len(eq) > 3:
                paper.append({
                    "question": f"Explain the theoretical components and significance of the following mathematical expression: {eq} (5 Marks)",
                    "marks": 5,
                    "answer_key": f"Answer should derive or break down the variables in {eq} based on the surrounding context."
                })
                continue
                
        words = p.split()
        if len(words) < 10: continue
        
        topic = "Concept"
        try:
            from backend.services.topic_extractor import extract_topics
            topics = [t.capitalize() for t in extract_topics(p) if len(t) > 3 and t.lower() not in stopwords and not re.search(r'[^a-zA-Z]', t)]
            if topics:
                topic = topics[0]
            else:
                topic = next((w.strip('.,!?:;()\'"*-') for w in words[len(words)//3:] if len(w) > 4 and w.lower() not in stopwords), "Concept").capitalize()
        except Exception:
            topic = next((w.strip('.,!?:;()\'"*-') for w in words[len(words)//3:] if len(w) > 4 and w.lower() not in stopwords), "Concept").capitalize()
            
        # Clean the paragraph of noisy source headers for the answer key
        p_clean = re.sub(r'--- Source:.*?---', '', p).strip()
        p_clean = re.sub(r'#.*?\n', '', p_clean).strip() # Remove markdown headers
            
        paper.append({
            "question": f"Define and briefly explain the significance of '{topic}' as discussed in the context. (5 Marks)",
            "marks": 5,
            "answer_key": f"The answer should mention: {p_clean[:300]}..."
        })

    # 2. 10-Mark Questions (Target 2)
    for p in content_paras[4:6]:
        if is_math_heavy:
            paper.append({
                "question": f"Provide a detailed mathematical derivation or proof relating to the following concept: {p[:100]}... Explain its primary mechanisms. (10 Marks)",
                "marks": 10,
                "answer_key": f"Key derivations and points to cover: {p[:400]}..."
            })
        else:
            paper.append({
                "question": f"Provide a detailed discussion on the following subject: {p[:100]}... Explaining its primary mechanisms and implications. (10 Marks)",
                "marks": 10,
                "answer_key": f"Key points to cover: {p[:400]}..."
            })

    # 3. 15-Mark Question (Target 1)
    if content_paras:
        p_final = content_paras[-1]
        if is_math_heavy:
            paper.append({
                "question": f"Conduct a comprehensive mathematical analysis focusing on the framework discussed here: {p_final[:150]}... Elaborate on the equations and practical outcomes. (15 Marks)",
                "marks": 15,
                "answer_key": f"Model Answer Structure: 1. Setup, 2. Derivation Analysis ({p_final[30:200]}), 3. Mathematical Implications ({p_final[200:400]})."
            })
        else:
            paper.append({
                "question": f"Conduct a comprehensive analysis of the concepts provided in this document, focusing specifically on: {p_final[:150]}... Elaborate on theoretical foundations and practical outcomes. (15 Marks)",
                "marks": 15,
                "answer_key": f"Model Answer Structure: 1. Introduction, 2. Core Analysis ({p_final[30:200]}), 3. Conclusion and Future Implications ({p_final[200:400]})."
            })

    return paper

def generate_quiz(text):
    """
    Generates distinct quiz questions across 3 difficulty levels.
    Prioritizes LLM-based generation if keys are available.
    """
    # 1. Clean the text from OCR noise, paths, and image placeholders
    text = clean_ocr_garbage(text)
    
    # 2. Try LLM-based generation first (High quality, handles math better)
    try:
        system_prompt = (
            "You are an expert academic examiner. Generate a quiz in JSON format with exactly 15 questions for each of the 3 difficulty levels: Foundation, Intermediate, and Expert Mastery. "
            "Ensure the questions are based ONLY on the provided text. Avoid using any path-like strings, image placeholders, or nonsensical OCR artifacts. "
            "For math questions, use LaTeX format (e.g., $E=mc^2$). "
            "Return ONLY the JSON object with the following structure: "
            '{"Foundation": [{"question": "...", "options": ["...", "..."], "answer": "..."}], "Intermediate": [...], "Expert Mastery": [...]}.'
        )
        
        # Limit context to avoid token limits
        context = text[:8000]
        response_text, provider = get_chat_response(
            prompt=f"Generate a quiz based on this text:\n\n{context}",
            system_prefix=system_prompt
        )
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            quiz_json = json.loads(json_match.group(0))
            if all(k in quiz_json for k in ["Foundation", "Intermediate", "Expert Mastery"]):
                return quiz_json
    except Exception as e:
        print(f"LLM Quiz Generation failed: {e}. Falling back to rule-based.")

    # 3. Fallback: Rule-based generation (Cleans text and avoids noise)
    # Be more lenient with sentence length to find more candidates
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if 20 < len(s.strip()) < 500]
    
    if not sentences:
        return {"Foundation": [], "Intermediate": [], "Expert Mastery": []}

    levels = {"Foundation": [], "Intermediate": [], "Expert Mastery": []}
    target_total = 45 # 15 questions * 3 levels
    all_qs = []
    
    # Pool of generic distractors
    pool = ["concept", "logic", "detail", "process", "approach", "result", "system", "theory", "method", "factor", "analysis", "context"]
    
    # 🔄 Loop until we have 45 questions or we've tried 100 times
    attempts = 0
    while len(all_qs) < target_total and attempts < 100:
        random.shuffle(sentences)
        for s in sentences:
            if len(all_qs) >= target_total: break
            
            words = s.split()
            if len(words) < 5: continue
            
            try:
                # Find valid words for blanks
                candidates = [w.strip('.,!?:;()[]{}"\'-') for w in words if len(w) > 4 and w.isalpha()]
                if not candidates: continue
                
                answer = random.choice(candidates)
                # Create the question
                question = re.sub(rf'\b{re.escape(answer)}\b', "_______", s, count=1, flags=re.IGNORECASE)
                
                if "_______" not in question or any(q['question'] == question for q in all_qs):
                    continue
                
                distractors = random.sample(pool, 3)
                options = list(set(distractors + [answer]))
                random.shuffle(options)
                
                all_qs.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                })
            except:
                continue
        attempts += 1

    # Distribute into levels
    for i, q in enumerate(all_qs):
        if i < 15: 
            q["question"] = f"(Foundation Level) {q['question']}"
            levels["Foundation"].append(q)
        elif i < 30:
            q["question"] = f"(Intermediate Level) {q['question']}"
            levels["Intermediate"].append(q)
        else:
            q["question"] = f"(Expert Mastery Level) {q['question']}"
            levels["Expert Mastery"].append(q)
            
    print(f"✅ Generated {len(all_qs)} questions via Fallback Engine.")
    return levels
