import firebase_admin
from firebase_admin import credentials, auth
import os
import json

def initialize_firebase():
    if not firebase_admin._apps:
        config_path = "database/firebase_config.json"
        
        # Check if file exists and is not empty
        if os.path.exists(config_path) and os.path.getsize(config_path) > 0:
            try:
                cred = credentials.Certificate(config_path)
                firebase_admin.initialize_app(cred)
                return True
            except Exception as e:
                print(f"Error initializing Firebase: {e}")
                return False
        else:
            # Fallback or alert user
            print("Firebase config not found or empty. Auth will be limited.")
            return False
    return True

def verify_user(email, password):
    # This is a placeholder for username/password verification
    # Firebase usually handles this client-side or via Identity Platform
    # For a simple demo/prototype, we can use a local mock or firebase auth REST API
    return True # Mock for now
