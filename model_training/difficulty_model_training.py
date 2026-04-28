import os
import re
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

# Paths
DATA_DIR = "data"
MODELS_DIR = "database/models"
MODEL_PATH = os.path.join(MODELS_DIR, "difficulty_classifier.pkl")

def estimate_difficulty_label(text):
    """
    Heuristic to generate initial labels for training.
    In a production app, these would come from user feedback.
    """
    word_count = len(text.split())
    unique_words = len(set(text.lower().split()))
    lexical_density = unique_words / (word_count + 1)
    
    # Advanced keywords
    complex_keywords = [
        'theory', 'analysis', 'hypothesis', 'framework', 'methodology', 
        'quantum', 'complex', 'advanced', 'comprehensive', 'stochastic'
    ]
    complex_matches = sum(1 for word in complex_keywords if word in text.lower())
    
    # Scoring
    score = (word_count * 0.001) + (complex_matches * 0.5) + (lexical_density * 10)
    
    if score < 5:
        return "Beginner"
    elif score < 15:
        return "Intermediate"
    else:
        return "Advanced"

def train_difficulty_model():
    """
    Trains a model to predict the difficulty level of a document.
    """
    if not os.path.exists(DATA_DIR):
        return "No data found for training."

    os.makedirs(MODELS_DIR, exist_ok=True)

    from backend.services.document_loader import load_document
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.docx', '.txt'))]
    
    if len(files) < 3:
        return "Need at least 3 documents to train the difficulty model."

    texts = []
    labels = []

    for file in files:
        try:
            path = os.path.join(DATA_DIR, file)
            content = load_document(path)
            if len(content.strip()) > 50:
                texts.append(content)
                # Generate a heuristic label for this document
                labels.append(estimate_difficulty_label(content))
        except Exception as e:
            print(f"Skipping {file}: {e}")

    if not texts:
        return "No valid text content found for difficulty training."

    # Create Pipeline for Difficulty Classification
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1500, stop_words='english')),
        ('classifier', RandomForestClassifier(n_estimators=100))
    ])

    # Train
    pipeline.fit(texts, labels)

    # Save
    joblib.dump(pipeline, MODEL_PATH)

    return f"Success! Difficulty model trained on {len(texts)} documents."

if __name__ == "__main__":
    import sys
    # Add project root to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    print(train_difficulty_model())
