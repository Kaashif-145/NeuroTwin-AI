import json
import os
import time

SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "database", "active_session.json")

def start_persistent_session(email):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    session_data = {
        "user_email": email,
        "expiry": time.time() + (24 * 3600) # 24 hours
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)

def get_persistent_session():
    if not os.path.exists(SESSION_FILE):
        return None
    
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            if time.time() < data["expiry"]:
                return data["user_email"]
            else:
                os.remove(SESSION_FILE)
                return None
    except:
        return None

def end_persistent_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

REMEMBER_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "database", "remember_me.json")

def save_remembered_user(email):
    os.makedirs(os.path.dirname(REMEMBER_FILE), exist_ok=True)
    with open(REMEMBER_FILE, "w") as f:
        json.dump({"last_email": email}, f)

def get_remembered_user():
    if os.path.exists(REMEMBER_FILE):
        try:
            with open(REMEMBER_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_email", "")
        except:
            return ""
    return ""
