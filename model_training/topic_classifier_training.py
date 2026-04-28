import os
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# Paths
DATA_DIR = "data"
MODELS_DIR = "database/models"
MODEL_PATH = os.path.join(MODELS_DIR, "topic_classifier.pkl")

def train_local_model():
    """
    Trains a simple MultinomialNB classifier on the documents in the data/ folder.
    This allows the 'NeuroTwin' to learn the specific topics the student is studying.
    """
    if not os.path.exists(DATA_DIR):
        return "No data found to train on."

    # Ensure model directory exists
    os.makedirs(MODELS_DIR, exist_ok=True)

    texts = []
    labels = []

    # In a real system, labels would be provided by user feedback.
    # For this 'Workable' version, we'll use the filenames as proxy labels or 
    # use the topic_extractor as a weak supervisor.
    from backend.services.topic_extractor import extract_topics
    from backend.services.document_loader import load_document

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.pdf', '.docx', '.txt'))]
    
    if len(files) < 2:
        return "Need at least 2 documents to train a meaningful local model."

    for file in files:
        try:
            path = os.path.join(DATA_DIR, file)
            content = load_document(path)
            
            # Use current AI as weak labeler for training the local personalization layer
            topics = extract_topics(content)
            if topics:
                main_topic = topics[0]
                texts.append(content)
                labels.append(main_topic)
        except Exception as e:
            print(f"Skipping {file}: {e}")

    if not texts:
        return "No processable text found."

    # Create Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('clf', MultinomialNB())
    ])

    # Train
    pipeline.fit(texts, labels)

    # Save
    joblib.dump(pipeline, MODEL_PATH)
    
    return f"Success! Trained on {len(texts)} documents. Your Twin is now personalized."

if __name__ == "__main__":
    import sys
    # Add project root to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    result = train_local_model()
    print(result)
