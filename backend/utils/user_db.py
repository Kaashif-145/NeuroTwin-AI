import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "users.json")

def load_users():
    if not os.path.exists(DB_PATH):
        # Ensure directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        # Default Admin
        default_users = {"admin@neurotwin.ai": "admin123", "mattokaasif145@gmail.com": "admin123"}
        with open(DB_PATH, "w") as f:
            json.dump(default_users, f)
        return default_users
    
    try:
        with open(DB_PATH, "r") as f:
            users = json.load(f)
            # Normalize keys to lowercase for consistency
            return {k.lower().strip(): v for k, v in users.items()}
    except:
        return {}

def save_user(email, password):
    email = email.lower().strip()
    users = load_users()
    users[email] = password
    with open(DB_PATH, "w") as f:
        json.dump(users, f)
