import json
import os
MEMORY_FILE = "./database/memory.json"
def save_user_memory(user_email, interaction_text):
    """ Saves a memory of the interaction to the User's memory. """
    if not os.path.exists("database"):
        os.makedirs("database")
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
    if user_email not in memory:
        memory[user_email] = []

    # Save the interaction
    memory[user_email].append(interaction_text)
    if len(memory[user_email]) > 10:
        memory[user_email].pop(0)
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)
    
def get_user_context(user_email):
    """ Retrieves all past context for this user."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
        if user_email in memory:
            return "\n".join(memory[user_email])
    return ""
    

        