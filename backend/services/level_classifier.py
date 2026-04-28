import re
import os
import joblib

MODEL_PATH = "database/models/difficulty_classifier.pkl"

def classify_level(text):
    """
    Classifies content as 'Beginner', 'Intermediate', or 'Advanced'.
    Uses a trained ML model if available, otherwise falls back to heuristics.
    """
    
    # 1. Try using the trained AI model
    if os.path.exists(MODEL_PATH):
        try:
            pipeline = joblib.load(MODEL_PATH)
            prediction = pipeline.predict([text])[0]
            return prediction
        except Exception as e:
            print(f"Error loading difficulty model: {e}")

    # 2. Fallback Heuristics (Generic complexity detection)
    college_keywords = [
        "thesis", "research", "undergraduate", "postgraduate", "university", 
        "dean", "faculty", "abstract", "methodology", "bibliography", 
        "advanced", "theoretical", "experimental", "symposium"
    ]
    
    school_keywords = [
        "grade", "homework", "class", "teacher", "primary", "secondary", 
        "kindergarten", "story", "simple", "lesson", "textbook", "quiz"
    ]
    
    text_lower = text.lower()
    
    college_score = sum(1 for word in college_keywords if word in text_lower)
    school_score = sum(1 for word in school_keywords if word in text_lower)
    
    # Heuristic: Longer complex words usually mean higher level
    long_words = len([w for w in re.findall(r'\b\w{10,}\b', text_lower)])
    college_score += (long_words / 10)
    
    if college_score > school_score:
        return "Advanced (College/Professional)"
    else:
        return "General (Foundation/School)"
