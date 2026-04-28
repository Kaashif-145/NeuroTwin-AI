import os
import json
import random
import time
from datetime import datetime

HISTORY_PATH = "database/upload_history.json"
PROFILE_PATH = "database/profiles.json"

def log_upload_history(file_names, ppt_path=None, pdf_path=None, user_email=None):
    """Logs the upload metadata to a persistent JSON archive."""
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    
    history = []
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    for name in file_names:
        # Prevent duplication: find if file already exists in history for THIS user
        existing_index = next((i for i, item in enumerate(history) if item["name"] == name and item.get("user_email") == user_email), None)
        
        # Preserve status and paths if it exists
        was_completed = False
        original_id = None
        existing_ppt = ppt_path
        existing_pdf = pdf_path
        
        if existing_index is not None:
            was_completed = history[existing_index].get("completed", False)
            original_id = history[existing_index].get("id")
            # If paths aren't provided now, keep old ones if they exist
            if not existing_ppt:
                existing_ppt = history[existing_index].get("ppt_path")
            if not existing_pdf:
                existing_pdf = history[existing_index].get("pdf_path")
            history.pop(existing_index)
            
        entry = {
            "name": name,
            "user_email": user_email,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(time.time()),
            "id": original_id if original_id else f"upload_{int(time.time())}_{random.randint(100, 999)}",
            "completed": was_completed,
            "ppt_path": existing_ppt,
            "pdf_path": existing_pdf
        }
        history.insert(0, entry) # Most recent first (either new or updated)
    
    # Keep only last 100 entries
    history = history[:100]
    
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)
    return history

def update_student_profile(topics):
    # Ensure directory exists
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    
    profile = {}
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r") as f:
                profile = json.load(f)
        except json.JSONDecodeError:
            profile = {}
            
    for topic in topics:
        if topic in profile:
            profile[topic] += 1
        else:
            profile[topic] = 1
            
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=4)

    return profile